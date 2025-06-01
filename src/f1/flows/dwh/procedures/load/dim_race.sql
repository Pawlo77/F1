CREATE OR ALTER PROCEDURE f1db.LoadDimRace
  @inserted_count INT OUTPUT,
  @updated_count INT OUTPUT
AS
BEGIN
  SET NOCOUNT ON;

  DECLARE @now DATETIME = GETDATE();
  DECLARE @merge_output TABLE (action_type NVARCHAR(10));
 	DECLARE @left_margin DATETIME;

  -- Get left_margin
  EXEC dwh.GetLeftMargin @process_name = 'DimRace', @left_margin = @left_margin OUTPUT;

    -- Prepare temporary table
  EXEC dwh.LoadDimRaceClearTables;

  -- Load source data into temporary table
  SELECT
    r.date AS race_date,
    r.time AS race_time,
    r.round AS race_round,
    gp.name AS race_grand_prix_name,
    gp.full_name AS race_grand_prix_full_name,
    gp.short_name AS race_grand_prix_short_name,
    gp.abbreviation AS race_grand_prix_abbreviation,
    r.official_name AS race_official_name,
    a.weekend_attendance AS race_weekend_attendance,
    r.qualifying_format AS race_qualifying_format,
    r.sprint_qualifying_format AS race_sprint_qualifying_format,
    dc.dwh_id AS circuit_id,
    c.turns AS race_turns,
    r.laps AS race_laps,
    r.distance AS race_distance,
    r.scheduled_laps AS race_scheduled_laps,
    r.scheduled_distance AS race_scheduled_distance,
    r.drivers_championship_decider AS race_drivers_championship_decider,
    r.constructors_championship_decider AS race_constructors_championship_decider,
    r.pre_qualifying_date AS race_pre_qualifying_date,
    r.pre_qualifying_time AS race_pre_qualifying_time,
    r.free_practice_1_date AS race_free_practice_1_date,
    r.free_practice_1_time AS race_free_practice_1_time,
    r.free_practice_2_date AS race_free_practice_2_date,
    r.free_practice_2_time AS race_free_practice_2_time,
    r.free_practice_3_date AS race_free_practice_3_date,
    r.free_practice_3_time AS race_free_practice_3_time,
    r.free_practice_4_date AS race_free_practice_4_date,
    r.free_practice_4_time AS race_free_practice_4_time,
    r.qualifying_1_date AS race_qualifying_1_date,
    r.qualifying_1_time AS race_qualifying_1_time,
    r.qualifying_2_date AS race_qualifying_2_date,
    r.qualifying_2_time AS race_qualifying_2_time,
    r.qualifying_date AS race_qualifying_date,
    r.qualifying_time AS race_qualifying_time,
    r.sprint_qualifying_date AS race_sprint_qualifying_date,
    r.sprint_qualifying_time AS race_sprint_qualifying_time,
    r.sprint_race_date AS race_sprint_race_date,
    r.sprint_race_time AS race_sprint_race_time,
    r.warming_up_date AS race_warming_up_date,
    r.warming_up_time AS race_warming_up_time,
    CONVERT(
      VARCHAR(96),
      HASHBYTES('MD5',
        CONCAT_WS('|',
          r.date, r.time, r.round, gp.name, gp.full_name, gp.short_name,
          gp.abbreviation, r.official_name, a.weekend_attendance,
          r.qualifying_format, r.sprint_qualifying_format, c.turns, r.laps, r.distance,
          r.scheduled_laps, r.scheduled_distance, r.drivers_championship_decider,
          r.constructors_championship_decider, r.pre_qualifying_date, r.pre_qualifying_time,
          r.free_practice_1_date, r.free_practice_1_time, r.free_practice_2_date, r.free_practice_2_time,
          r.free_practice_3_date, r.free_practice_3_time, r.free_practice_4_date, r.free_practice_4_time,
          r.qualifying_1_date, r.qualifying_1_time, r.qualifying_2_date, r.qualifying_2_time,
          r.qualifying_date, r.qualifying_time, r.sprint_qualifying_date, r.sprint_qualifying_time,
          r.sprint_race_date, r.sprint_race_time, r.warming_up_date, r.warming_up_time
        )
      ),
      2
    ) AS dwh_hash,
    COALESCE(c.dwh_valid_to, r.dwh_valid_to, gp.dwh_valid_to, a.dwh_valid_to) AS dwh_valid_to
  INTO #src__LoadDimRace
  FROM f1db.race r
  JOIN f1db.circuit c ON r.circuit_id = c.id
  JOIN dwh.dim_circuit dc ON dc.circuit_full_name = c.full_name
  JOIN f1db.grand_prix gp ON r.grand_prix_id = gp.id
  LEFT JOIN web.attendance a
    ON a.race = CASE
        WHEN LOWER(gp.full_name) = 'malaysian grand prix' THEN CAST(r.year AS VARCHAR) + ' Malaysia Grand Prix'
        WHEN LOWER(gp.full_name) = 'mexican grand prix' AND r.year > 2020 THEN CAST(r.year AS VARCHAR) + ' Mexico City Grand Prix'
        WHEN LOWER(gp.full_name) = 'united states grand prix' AND r.year < 2017 THEN CAST(r.year AS VARCHAR) + ' US Grand Prix'
        WHEN LOWER(gp.full_name) = 'sÃ£o paulo grand prix' THEN CAST(r.year AS VARCHAR) + ' Sao Paulo Grand Prix'
        WHEN LOWER(gp.full_name) = '70th anniversary grand prix' THEN gp.full_name
        ELSE CAST(r.year AS VARCHAR) + ' ' + gp.full_name
      END
  WHERE GREATEST(r.dwh_modified_at, c.dwh_modified_at, gp.dwh_modified_at) > DATEADD(MINUTE, -5, @left_margin);

 	-- create index on tmp table
	CREATE INDEX idx__src__LoadDimRace ON #src__LoadDimRace(race_date);

  -- Merge into the dimension table
  MERGE dwh.dim_race AS dr
  USING #src__LoadDimRace AS src
  ON dr.race_date = src.race_date

  WHEN MATCHED AND (
    src.dwh_hash <> dr.dwh_hash OR
    (src.dwh_valid_to IS NOT NULL AND dr.dwh_valid_to IS NULL)
  )
  THEN UPDATE SET
  		dr.race_grand_prix_name = src.race_grand_prix_name,
  		dr.race_grand_prix_full_name = src.race_grand_prix_full_name,
  		dr.race_grand_prix_short_name = src.race_grand_prix_short_name,
  		dr.race_grand_prix_abbreviation = src.race_grand_prix_abbreviation,
  		dr.race_official_name = src.race_official_name,
    dr.dwh_hash = src.dwh_hash,
    dr.dwh_modified_at = @now,
    dr.dwh_valid_to = CASE
      WHEN src.dwh_valid_to IS NOT NULL AND dr.dwh_valid_to IS NULL THEN @now
      ELSE NULL
    END

  WHEN NOT MATCHED BY TARGET THEN
    INSERT (
      race_date, race_time, race_round,
      race_grand_prix_name, race_grand_prix_full_name, race_grand_prix_short_name,
      race_grand_prix_abbreviation, race_official_name, race_weekend_attendance,
      race_qualifying_format, race_sprint_qualifying_format, circuit_id,
      race_turns, race_laps, race_distance, race_scheduled_laps, race_scheduled_distance,
      race_drivers_championship_decider, race_constructors_championship_decider,
      race_pre_qualifying_date, race_pre_qualifying_time,
      race_free_practice_1_date, race_free_practice_1_time,
      race_free_practice_2_date, race_free_practice_2_time,
      race_free_practice_3_date, race_free_practice_3_time,
      race_free_practice_4_date, race_free_practice_4_time,
      race_qualifying_1_date, race_qualifying_1_time,
      race_qualifying_2_date, race_qualifying_2_time,
      race_qualifying_date, race_qualifying_time,
      race_sprint_qualifying_date, race_sprint_qualifying_time,
      race_sprint_race_date, race_sprint_race_time,
      race_warming_up_date, race_warming_up_time,
      dwh_hash, dwh_valid_from, dwh_modified_at, dwh_valid_to
    )
    VALUES (
      src.race_date, src.race_time, src.race_round,
      src.race_grand_prix_name, src.race_grand_prix_full_name, src.race_grand_prix_short_name,
      src.race_grand_prix_abbreviation, src.race_official_name, src.race_weekend_attendance,
      src.race_qualifying_format, src.race_sprint_qualifying_format, src.circuit_id,
      src.race_turns, src.race_laps, src.race_distance, src.race_scheduled_laps, src.race_scheduled_distance,
      src.race_drivers_championship_decider, src.race_constructors_championship_decider,
      src.race_pre_qualifying_date, src.race_pre_qualifying_time,
      src.race_free_practice_1_date, src.race_free_practice_1_time,
      src.race_free_practice_2_date, src.race_free_practice_2_time,
      src.race_free_practice_3_date, src.race_free_practice_3_time,
      src.race_free_practice_4_date, src.race_free_practice_4_time,
      src.race_qualifying_1_date, src.race_qualifying_1_time,
      src.race_qualifying_2_date, src.race_qualifying_2_time,
      src.race_qualifying_date, src.race_qualifying_time,
      src.race_sprint_qualifying_date, src.race_sprint_qualifying_time,
      src.race_sprint_race_date, src.race_sprint_race_time,
      src.race_warming_up_date, src.race_warming_up_time,
      src.dwh_hash, @now, @now, NULL
    )

  OUTPUT $action INTO @merge_output;

 	-- Count inserted and updated rows
  SELECT
    @inserted_count = ISNULL(SUM(CASE WHEN action_type = 'INSERT' THEN 1 ELSE 0 END), 0),
    @updated_count = ISNULL(SUM(CASE WHEN action_type = 'UPDATE' THEN 1 ELSE 0 END), 0)
  FROM @merge_output;

  -- Log this run
	EXEC dwh.LogEtlRun
	  @process_name = 'DimRace',
	  @inserted_count = @inserted_count,
	  @updated_count = @updated_count;
	EXEC dwh.SetLeftMargin
	  @process_name = 'DimRace',
	  @last_run_at = @now;

  -- Clean up
  EXEC dwh.LoadDimRaceClearTables;
END;
