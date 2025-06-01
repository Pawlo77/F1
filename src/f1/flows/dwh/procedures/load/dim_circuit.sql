CREATE OR ALTER PROCEDURE f1db.LoadDimCircuit
  @inserted_count INT OUTPUT,
  @updated_count INT OUTPUT
AS
BEGIN
  SET NOCOUNT ON;

  DECLARE @now DATETIME = GETDATE();
  DECLARE @merge_output TABLE (action_type NVARCHAR(10));
	DECLARE @left_margin DATETIME;

  -- Get left_margin
	EXEC dwh.GetLeftMargin @process_name = 'DimCircuit', @left_margin = @left_margin OUTPUT;

  -- Prepare temporary table
  EXEC dwh.LoadDimCircuitClearTables;

  -- Load source data into temporary table
  SELECT
    dc.dwh_id AS country_id,
    c.name AS circuit_name,
    c.full_name AS circuit_full_name,
    c.type AS circuit_type,
    c.direction AS circuit_direction,
    c.place_name AS circuit_place_name,
    c.latitude AS circuit_latitude,
    c.longitude AS circuit_longitude,
    c.length AS circuit_length,
    cd.rating AS circuit_rating,
    cd.reviews_num AS circuit_reviews_num,
    cd.website AS circuit_website,
    CONVERT(
      VARCHAR(96),
      HASHBYTES('MD5',
        CONCAT_WS('|',
          c.name,
          c.full_name,
          c.type,
          c.direction,
          c.place_name,
          c.latitude,
          c.longitude,
          c.length,
          cd.rating,
          cd.reviews_num,
          cd.website
        )
      ),
      2
    ) AS dwh_hash,
    COALESCE(c.dwh_valid_to, co.dwh_valid_to, cd.dwh_valid_to, dc.dwh_valid_to) AS dwh_valid_to
  INTO #src__LoadDimCircuit
  FROM f1db.country co
  JOIN f1db.circuit c ON co.id = c.country_id
  CROSS APPLY (
    SELECT TOP 1 cd.*
    FROM web.circuits_details cd
    WHERE LOWER(cd.tags) LIKE '%fia%'
    ORDER BY
      POWER(SIN(RADIANS(cd.latitude - c.latitude) / 2), 2) +
      COS(RADIANS(c.latitude)) * COS(RADIANS(cd.latitude)) *
      POWER(SIN(RADIANS(cd.longitude - c.longitude) / 2), 2)
  ) AS cd
  JOIN dwh.dim_country dc ON co.name = dc.country_name
  WHERE GREATEST(co.dwh_modified_at, c.dwh_modified_at, cd.dwh_modified_at) > DATEADD(MINUTE, -5, @left_margin);

	-- create index on tmp table
	CREATE INDEX idx__src__LoadDimCircuit ON #src__LoadDimCircuit(circuit_full_name);

  -- Merge into the dimension table
  MERGE dwh.dim_circuit AS dc
  USING #src__LoadDimCircuit AS src
  ON dc.circuit_full_name = src.circuit_full_name

  WHEN MATCHED AND (
    src.dwh_hash <> dc.dwh_hash OR
    (src.dwh_valid_to IS NOT NULL AND dc.dwh_valid_to IS NULL)
  )
  THEN UPDATE SET
  		dc.circuit_name = src.circuit_name,
    dc.circuit_type = src.circuit_type,
    dc.circuit_direction = src.circuit_direction,
    dc.circuit_place_name = src.circuit_place_name,
    dc.circuit_length = src.circuit_length,
    dc.circuit_rating = src.circuit_rating,
    dc.circuit_reviews_num = src.circuit_reviews_num,
    dc.circuit_website = src.circuit_website,
    dc.country_id = src.country_id,
    dc.dwh_hash = src.dwh_hash,
    dc.dwh_modified_at = @now,
    dc.dwh_valid_to = CASE
      WHEN src.dwh_valid_to IS NOT NULL AND dc.dwh_valid_to IS NULL THEN @now
      ELSE NULL
    END

  WHEN NOT MATCHED BY TARGET THEN
    INSERT (
      country_id,
      circuit_name,
      circuit_full_name,
      circuit_type,
      circuit_direction,
      circuit_place_name,
      circuit_latitude,
      circuit_longitude,
      circuit_length,
      circuit_rating,
      circuit_reviews_num,
      circuit_website,
      dwh_hash,
      dwh_valid_from,
      dwh_modified_at,
      dwh_valid_to
    )
    VALUES (
      src.country_id,
      src.circuit_name,
      src.circuit_full_name,
      src.circuit_type,
      src.circuit_direction,
      src.circuit_place_name,
      src.circuit_latitude,
      src.circuit_longitude,
      src.circuit_length,
      src.circuit_rating,
      src.circuit_reviews_num,
      src.circuit_website,
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
	  @process_name = 'DimCircuit',
	  @inserted_count = @inserted_count,
	  @updated_count = @updated_count;
	EXEC dwh.SetLeftMargin
	  @process_name = 'DimCircuit',
	  @last_run_at = @now;

  -- Clean up
  EXEC dwh.LoadDimCircuitClearTables;
END;
