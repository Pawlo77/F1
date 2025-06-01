CREATE OR ALTER PROCEDURE f1db.LoadDimCountry
  @inserted_count INT OUTPUT,
  @updated_count INT OUTPUT
AS
BEGIN
  SET NOCOUNT ON;

  DECLARE @now DATETIME = GETDATE();
  DECLARE @merge_output TABLE (action_type NVARCHAR(10));
  DECLARE @left_margin DATETIME;

  -- Get left_margin
	EXEC dwh.GetLeftMargin @process_name = 'DimCountry', @left_margin = @left_margin OUTPUT;

  -- Prepare temp table
  EXEC dwh.LoadDimCountryClearTables;

  -- Load data from source tables
  SELECT
    co.alpha2_code AS country_alpha2_code,
    co.alpha3_code AS country_alpha3_code,
    co.name AS country_name,
    co.demonym AS country_demonym,
    ct.name AS continent_name,
    ct.code AS continent_code,
    ct.demonym AS continent_demonym,
    CONVERT(
      VARCHAR(96),
      HASHBYTES('MD5',
        CONCAT_WS('|',
          co.alpha2_code,
          co.alpha3_code,
          co.name,
          co.demonym,
          ct.name,
          ct.code,
          ct.demonym
        )
      ),
      2
    ) AS dwh_hash,
    COALESCE(co.dwh_valid_to, ct.dwh_valid_to) AS dwh_valid_to
  INTO #src__LoadDimCountry
  FROM f1db.country co
  JOIN f1db.continent ct ON co.continent_id = ct.id
  WHERE GREATEST(co.dwh_modified_at, ct.dwh_modified_at) > DATEADD(MINUTE, -5, @left_margin);

 	-- create index on tmp table
	CREATE INDEX idx__src__LoadDimCountry ON #src__LoadDimCountry(country_name);

  -- check if any data has changed even tho it shouldn't have
  IF EXISTS (
    SELECT 1
    FROM #src__LoadDimCountry src
    INNER JOIN dwh.dim_country dc ON dc.country_name = src.country_name
    WHERE dc.dwh_hash <> src.dwh_hash
  )
  BEGIN
    THROW 50000, 'dwh_hash has changed for one or more records', 1;
  END;

  -- Merge into the dimension table
  MERGE dwh.dim_country AS dc
  USING #src__LoadDimCountry AS src
  ON dc.country_name = src.country_name

  WHEN MATCHED AND (
    src.dwh_valid_to IS NOT NULL AND dc.dwh_valid_to IS NULL
  )
  THEN UPDATE SET
    dc.dwh_modified_at = @now,
    dc.dwh_valid_to = @now

  WHEN NOT MATCHED BY TARGET THEN
    INSERT (
      country_alpha2_code,
      country_alpha3_code,
      country_name,
      country_demonym,
      continent_name,
      continent_code,
      continent_demonym,
      dwh_hash,
      dwh_valid_from,
      dwh_modified_at,
      dwh_valid_to
    )
    VALUES (
      src.country_alpha2_code,
      src.country_alpha3_code,
      src.country_name,
      src.country_demonym,
      src.continent_name,
      src.continent_code,
      src.continent_demonym,
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
	  @process_name = 'DimCountry',
	  @inserted_count = @inserted_count,
	  @updated_count = @updated_count;
	EXEC dwh.SetLeftMargin
	  @process_name = 'DimCountry',
	  @last_run_at = @now;

  -- Clean up
  EXEC dwh.LoadDimCountryClearTables;
END;
