CREATE OR ALTER PROCEDURE f1db.LoadDimDriver
  @inserted_count INT OUTPUT,
  @updated_count INT OUTPUT
AS
BEGIN
  SET NOCOUNT ON;

  DECLARE @now DATETIME = GETDATE();
  DECLARE @merge_output TABLE (action_type NVARCHAR(10));
	DECLARE @left_margin DATETIME;

    -- Get left_margin
	EXEC dwh.GetLeftMargin @process_name = 'DimDriver', @left_margin = @left_margin OUTPUT;

  -- Prepare temp table
  EXEC dwh.LoadDimDriverClearTables;

  -- Load source data into temporary table
  SELECT
    d.name AS driver_name,
    d.first_name AS driver_first_name,
    d.last_name AS driver_last_name,
    d.full_name AS driver_full_name,
    d.abbreviation AS driver_abbreviation,
    d.permanent_number AS driver_permanent_number,
    d.gender AS driver_gender,
    d.date_of_birth AS driver_date_of_birth,
    d.date_of_death AS driver_date_of_death,
    d.place_of_birth AS driver_place_of_birth,
    dc1.dwh_id AS driver_country_of_birth_country_id,
    dc2.dwh_id AS driver_nationality_country_id,
    dc3.dwh_id AS driver_second_nationality_country_id,
    CONVERT(
      VARCHAR(96),
      HASHBYTES('MD5',
        CONCAT_WS('|',
          d.name,
          d.first_name,
          d.last_name,
          d.full_name,
          d.abbreviation,
          d.permanent_number,
          d.gender,
          d.date_of_birth,
          d.date_of_death,
          d.place_of_birth,
          dc1.dwh_id,
          dc2.dwh_id,
          dc3.dwh_id
        )
      ),
      2
    ) AS dwh_hash,
    COALESCE(d.dwh_valid_to, dc1.dwh_valid_to, dc2.dwh_valid_to, dc3.dwh_valid_to) AS dwh_valid_to
  INTO #src__LoadDimDriver
  FROM f1db.driver d
  JOIN f1db.country c1 ON d.country_of_birth_country_id = c1.id
  JOIN dwh.dim_country dc1 ON c1.name = dc1.country_name
  JOIN f1db.country c2 ON d.nationality_country_id = c2.id
  JOIN dwh.dim_country dc2 ON c2.name = dc2.country_name
  LEFT JOIN f1db.country c3 ON d.second_nationality_country_id = c3.id
  LEFT JOIN dwh.dim_country dc3 ON c3.name = dc3.country_name
  WHERE GREATEST(d.dwh_modified_at, c1.dwh_modified_at, c2.dwh_modified_at, c3.dwh_modified_at) > DATEADD(MINUTE, -5, @left_margin);

  	-- create index on tmp table
	CREATE INDEX idx__src__LoadDimDriver ON #src__LoadDimDriver(driver_full_name);

  -- Merge into the dimension table
  MERGE dwh.dim_driver AS dd
  USING #src__LoadDimDriver AS src
  ON dd.driver_full_name = src.driver_full_name

	WHEN MATCHED AND (
    src.dwh_hash <> dd.dwh_hash OR
    (src.dwh_valid_to IS NOT NULL AND dd.dwh_valid_to IS NULL)
  )
  THEN UPDATE SET
    dd.driver_name = src.driver_name,
		dd.driver_abbreviation = src.driver_abbreviation,
		dd.driver_permanent_number = src.driver_permanent_number,
		dd.driver_date_of_death = src.driver_date_of_death,
    dd.dwh_hash = src.dwh_hash,
    dd.dwh_modified_at = @now,
    dd.dwh_valid_to = CASE
      WHEN src.dwh_valid_to IS NOT NULL AND dd.dwh_valid_to IS NULL THEN @now
      ELSE NULL
    END

  WHEN NOT MATCHED BY TARGET THEN
    INSERT (
      driver_name,
      driver_first_name,
      driver_last_name,
      driver_full_name,
      driver_abbreviation,
      driver_permanent_number,
      driver_gender,
      driver_date_of_birth,
      driver_date_of_death,
      driver_place_of_birth,
      driver_country_of_birth_country_id,
      driver_nationality_country_id,
      driver_second_nationality_country_id,
      dwh_hash,
      dwh_valid_from,
      dwh_modified_at,
      dwh_valid_to
    )
    VALUES (
      src.driver_name,
      src.driver_first_name,
      src.driver_last_name,
      src.driver_full_name,
      src.driver_abbreviation,
      src.driver_permanent_number,
      src.driver_gender,
      src.driver_date_of_birth,
      src.driver_date_of_death,
      src.driver_place_of_birth,
      src.driver_country_of_birth_country_id,
      src.driver_nationality_country_id,
      src.driver_second_nationality_country_id,
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
	  @process_name = 'DimDriver',
	  @inserted_count = @inserted_count,
	  @updated_count = @updated_count;
	EXEC dwh.SetLeftMargin
	  @process_name = 'DimDriver',
	  @last_run_at = @now;

  -- Clean up
    EXEC dwh.LoadDimDriverClearTables;
END;
