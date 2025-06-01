CREATE OR ALTER PROCEDURE f1db.LoadDimConstructor
  @inserted_count INT OUTPUT,
  @updated_count INT OUTPUT
AS
BEGIN
  SET NOCOUNT ON;

  DECLARE @now DATETIME = GETDATE();
  DECLARE @merge_output TABLE (action_type NVARCHAR(10));
	DECLARE @left_margin DATETIME;

-- Get left_margin
	EXEC dwh.GetLeftMargin @process_name = 'DimConstructor', @left_margin = @left_margin OUTPUT;

  -- Prepare temp table
  EXEC dwh.LoadDimConstructorClearTables;

  -- Load data from source tables
  SELECT
    c.name AS constructor_name,
    c.full_name AS constructor_full_name,
    dc.dwh_id AS country_id,
		CONVERT(
      VARCHAR(96),
      HASHBYTES('MD5',
        CONCAT_WS('|',
          c.name,
          c.full_name,
          dc.dwh_id
        )
      ),
      2
    ) AS dwh_hash,
    COALESCE(c.dwh_valid_to, dc.dwh_valid_to) AS dwh_valid_to
  INTO #src__LoadDimConstructor
  FROM f1db.constructor c
  JOIN f1db.country AS co ON c.country_id = co.id
  JOIN dwh.dim_country dc ON co.name = dc.country_name
  WHERE GREATEST(c.dwh_modified_at, co.dwh_modified_at) > DATEADD(MINUTE, -5, @left_margin);

  -- create index on tmp table
	CREATE INDEX idx__src__LoadDimConstructor ON #src__LoadDimConstructor(constructor_full_name, constructor_name);

  -- Merge into the dimension table
  MERGE dwh.dim_constructor AS dc
  USING #src__LoadDimConstructor AS src
  ON dc.constructor_full_name = src.constructor_full_name
  AND dc.constructor_name = src.constructor_name

  WHEN MATCHED AND (
    src.dwh_hash <> dc.dwh_hash OR
    (src.dwh_valid_to IS NOT NULL AND dc.dwh_valid_to IS NULL)
  )
  THEN UPDATE SET
    dc.country_id = src.country_id,
    dc.dwh_hash = src.dwh_hash,
    dc.dwh_modified_at = @now,
    dc.dwh_valid_to = CASE
      WHEN src.dwh_valid_to IS NOT NULL AND dc.dwh_valid_to IS NULL THEN @now
      ELSE NULL
    END

  WHEN NOT MATCHED BY TARGET THEN
    INSERT (
      constructor_name,
      constructor_full_name,
      country_id,
      dwh_hash,
      dwh_valid_from,
      dwh_modified_at,
      dwh_valid_to
    )
    VALUES (
      src.constructor_name,
      src.constructor_full_name,
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
	  @process_name = 'DimConstructor',
	  @inserted_count = @inserted_count,
	  @updated_count = @updated_count;
	EXEC dwh.SetLeftMargin
	  @process_name = 'DimConstructor',
	  @last_run_at = @now;

  -- Clean up
  EXEC dwh.LoadDimConstructorClearTables;
END;
