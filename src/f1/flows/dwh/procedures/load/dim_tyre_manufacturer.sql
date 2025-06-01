CREATE OR ALTER PROCEDURE f1db.LoadDimTyreManufacturer
  @inserted_count INT OUTPUT,
  @updated_count INT OUTPUT
AS
BEGIN
  SET NOCOUNT ON;

  DECLARE @now DATETIME = GETDATE();
  DECLARE @merge_output TABLE (action_type NVARCHAR(10));
	DECLARE @left_margin DATETIME;

  -- Get left_margin
  EXEC dwh.GetLeftMargin @process_name = 'DimTyreManufacturer', @left_margin = @left_margin OUTPUT;

  -- Prepare temp table
  EXEC dwh.LoadDimTyreManufacturerClearTables;

  -- Load data from source tables
  SELECT
    tm.name AS tyre_manufacturer_name,
    dc.dwh_id AS country_id,
    CONVERT(
      VARCHAR(96),
      HASHBYTES('MD5',
        CONCAT_WS('|',
          tm.name,
          dc.dwh_id
        )
      ),
      2
    ) AS dwh_hash,
    COALESCE(tm.dwh_valid_to, dc.dwh_valid_to) AS dwh_valid_to
  INTO #src__LoadDimTyreManufacturer
  FROM f1db.tyre_manufacturer tm
  JOIN f1db.country co ON tm.country_id = co.id
  JOIN dwh.dim_country dc ON co.name = dc.country_name
  WHERE GREATEST(tm.dwh_modified_at, co.dwh_modified_at) > DATEADD(MINUTE, -5, @left_margin);

 	-- create index on tmp table
	CREATE INDEX idx__src__LoadDimTyreManufacturer ON #src__LoadDimTyreManufacturer(tyre_manufacturer_name);

 	-- check if any data has changed even tho it shouldn't have
  IF EXISTS (
    SELECT 1
    FROM #src__LoadDimTyreManufacturer src
    INNER JOIN dwh.dim_tyre_manufacturer dtm ON dtm.tyre_manufacturer_name = src.tyre_manufacturer_name
    WHERE dtm.dwh_hash <> src.dwh_hash
  )
  BEGIN
    THROW 50002, 'dwh_hash has changed for one or more tyre manufacturer records', 1;
  END;

  -- Merge into the dimension table
  MERGE dwh.dim_tyre_manufacturer AS dtm
  USING #src__LoadDimTyreManufacturer AS src
  ON dtm.tyre_manufacturer_name = src.tyre_manufacturer_name

  WHEN MATCHED AND (
    src.dwh_valid_to IS NOT NULL AND dtm.dwh_valid_to IS NULL
  )
  THEN UPDATE SET
    dtm.dwh_modified_at = @now,
    dtm.dwh_valid_to = @now

  WHEN NOT MATCHED BY TARGET THEN
    INSERT (
      tyre_manufacturer_name,
      country_id,
      dwh_hash,
      dwh_valid_from,
      dwh_modified_at,
      dwh_valid_to
    )
    VALUES (
      src.tyre_manufacturer_name,
      src.country_id,
      src.dwh_hash,
      @now,
      @now,
      NULL
    )

  OUTPUT $action INTO @merge_output;

  -- Count inserted and updated rows
  SELECT
    @inserted_count = ISNULL(SUM(CASE WHEN action_type = 'INSERT' THEN 1 ELSE 0 END), 0),
    @updated_count = ISNULL(SUM(CASE WHEN action_type = 'UPDATE' THEN 1 ELSE 0 END), 0)
  FROM @merge_output;


  -- Log this run
	EXEC dwh.LogEtlRun
	  @process_name = 'DimTyreManufacturer',
	  @inserted_count = @inserted_count,
	  @updated_count = @updated_count;
	EXEC dwh.SetLeftMargin
	  @process_name = 'DimTyreManufacturer',
	  @last_run_at = @now;

  -- Clean up
  EXEC dwh.LoadDimTyreManufacturerClearTables;
END;
