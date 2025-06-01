CREATE OR ALTER PROCEDURE f1db.LoadDimEngineManufacturer
  @inserted_count INT OUTPUT,
  @updated_count INT OUTPUT
AS
BEGIN
  SET NOCOUNT ON;

  DECLARE @now DATETIME = GETDATE();
  DECLARE @merge_output TABLE (action_type NVARCHAR(10));
	DECLARE @left_margin DATETIME;

  -- Get left_margin
  EXEC dwh.GetLeftMargin @process_name = 'DimEngineManufacturer', @left_margin = @left_margin OUTPUT;

  -- Prepare temp table
  EXEC dwh.LoadDimEngineManufacturerClearTables;

  -- Load data from source tables
  SELECT
    em.name AS engine_name,
    dc.dwh_id AS country_id,
		CONVERT(
      VARCHAR(96),
      HASHBYTES('MD5',
        CONCAT_WS('|',
          em.name,
          dc.dwh_id
        )
      ),
      2
    ) AS dwh_hash,
    COALESCE(em.dwh_valid_to, dc.dwh_valid_to) AS dwh_valid_to
  INTO #src__LoadDimEngineManufacturer
  FROM f1db.engine_manufacturer em
  JOIN f1db.country co ON em.country_id = co.id
  JOIN dwh.dim_country dc ON co.name = dc.country_name
  WHERE GREATEST(co.dwh_modified_at, em.dwh_modified_at) > DATEADD(MINUTE, -5, @left_margin);

	-- create index on tmp table
	CREATE INDEX idx__src__LoadDimEngineManufacturer ON #src__LoadDimEngineManufacturer(engine_name);

 	-- check if any data has changed even tho it shouldn't have
  IF EXISTS (
    SELECT 1
    FROM #src__LoadDimEngineManufacturer src
    INNER JOIN dwh.dim_engine_manufacturer dem ON dem.engine_name = src.engine_name
    WHERE dem.dwh_hash <> src.dwh_hash
  )
  BEGIN
    THROW 50001, 'dwh_hash has changed for one or more engine manufacturer records', 1;
  END;

  -- Merge into the dimension table
  MERGE dwh.dim_engine_manufacturer AS dem
  USING #src__LoadDimEngineManufacturer AS src
  ON dem.engine_name = src.engine_name

  WHEN MATCHED AND (
    src.dwh_valid_to IS NOT NULL AND dem.dwh_valid_to IS NULL
  )
  THEN UPDATE SET
    dem.dwh_modified_at = @now,
    dem.dwh_valid_to = @now

  WHEN NOT MATCHED BY TARGET THEN
    INSERT (
      engine_name,
      country_id,
      dwh_hash,
      dwh_valid_from,
      dwh_modified_at,
      dwh_valid_to
    )
    VALUES (
      src.engine_name,
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
	  @process_name = 'DimEngineManufacturer',
	  @inserted_count = @inserted_count,
	  @updated_count = @updated_count;
	EXEC dwh.SetLeftMargin
	  @process_name = 'DimEngineManufacturer',
	  @last_run_at = @now;

  -- Clean up
  EXEC dwh.LoadDimEngineManufacturerClearTables;
END;
