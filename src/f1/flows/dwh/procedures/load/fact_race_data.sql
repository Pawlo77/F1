CREATE OR ALTER PROCEDURE f1db.LoadFactRaceData
    @inserted_count INT OUTPUT,
    @updated_count INT OUTPUT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @now DATETIME = GETDATE();
    DECLARE @merge_output TABLE (action_type NVARCHAR(10));
        DECLARE @left_margin DATETIME;

    -- Get left_margin
    EXEC dwh.GetLeftMargin @process_name = 'FactRaceData', @left_margin = @left_margin OUTPUT;

	-- Prepare temporary table
	EXEC dwh.LoadFactRaceDataClearTables;

	-- race_info
	SELECT
        dr.dwh_id AS race_id,
        r.id AS id,
		r.dwh_valid_to AS dwh_valid_to,
        r.dwh_modified_at AS dwh_modified_at
	INTO #race_info__LoadFactRaceData
	FROM f1db.race r
	JOIN dwh.dim_race dr
    ON dr.race_date = r.date;

	-- driver_info
    SELECT
        dd.dwh_id AS driver_id,
        d.id AS id,
        d.dwh_valid_to AS dwh_valid_to,
        d.dwh_modified_at AS dwh_modified_at
	INTO #driver_info__LoadFactRaceData
	FROM f1db.driver d
	JOIN dwh.dim_driver dd ON dd.driver_full_name = d.full_name AND dd.driver_date_of_birth = d.date_of_birth;

	-- constructor_info
	SELECT
		dct.dwh_id AS constructor_id,
        c.id AS id,
        c.dwh_valid_to AS dwh_valid_to,
        c.dwh_modified_at AS dwh_modified_at
	INTO #constructor_info__LoadFactRaceData
	FROM f1db.constructor c
	JOIN dwh.dim_constructor dct ON dct.constructor_name = c.name AND dct.constructor_full_name = c.full_name;

	-- engine_info
	SELECT
		dem.dwh_id AS engine_manufacturer_id,
        em.id AS id,
        em.dwh_valid_to AS dwh_valid_to,
        em.dwh_modified_at AS dwh_modified_at
	INTO #engine_info__LoadFactRaceData
	FROM f1db.engine_manufacturer em
	JOIN dwh.dim_engine_manufacturer dem ON dem.engine_name = em.name;

	-- tyre_info
	SELECT
		dtm.dwh_id AS tyre_manufacturer_id,
        tm.id AS id,
        tm.dwh_valid_to AS dwh_valid_to,
        tm.dwh_modified_at AS dwh_modified_at
	INTO #tyre_info__LoadFactRaceData
	FROM f1db.tyre_manufacturer tm
	JOIN dwh.dim_tyre_manufacturer dtm ON dtm.tyre_manufacturer_name = tm.name;

	-- create indexes on tmp tables
	CREATE INDEX idx__tyre_info__LoadFactRaceData ON #tyre_info__LoadFactRaceData(id);
	CREATE INDEX idx__driver_info__LoadFactRaceData ON #driver_info__LoadFactRaceData(id);
	CREATE INDEX idx__constructor_info__LoadFactRaceData ON #constructor_info__LoadFactRaceData(id);
	CREATE INDEX idx__engine_info__LoadFactRaceData ON #engine_info__LoadFactRaceData(id);
	CREATE INDEX idx__engine_info__LoadFactRaceData ON #race_info__LoadFactRaceData(id);

	-- main select
	SELECT
		ri.race_id AS race_id,
        rd.type AS race_data_type,
        rd.position_display_order AS race_data_position_display_order,
        rd.position_number AS race_data_position_number,
        rd.position_text AS race_data_position_text,
        rd.driver_number AS race_data_driver_number,
        di.driver_id AS driver_id,
        ci.constructor_id AS constructor_id,
        ei.engine_manufacturer_id AS engine_manufacturer_id,
        ti.tyre_manufacturer_id AS tyre_manufacturer_id,
        rd.practice_time_millis AS race_data_practice_time_millis,
        rd.practice_gap_millis AS race_data_practice_gap_millis,
        rd.practice_interval_millis AS race_data_practice_interval_millis,
        rd.practice_laps AS race_data_practice_laps,
        rd.qualifying_time_millis AS race_data_qualifying_time_millis,
        rd.qualifying_q1_millis AS race_data_qualifying_q1_millis,
        rd.qualifying_q2_millis AS race_data_qualifying_q2_millis,
        rd.qualifying_q3_millis AS race_data_qualifying_q3_millis,
        rd.qualifying_gap_millis AS race_data_qualifying_gap_millis,
        rd.qualifying_interval_millis AS race_data_qualifying_interval_millis,
        rd.qualifying_laps AS race_data_qualifying_laps,
        rd.starting_grid_position_qualification_position_number AS race_data_starting_grid_position_qualification_position_number,
        rd.starting_grid_position_qualification_position_text AS race_data_starting_grid_position_qualification_position_text,
        rd.starting_grid_position_grid_penalty AS race_data_starting_grid_position_grid_penalty,
        rd.starting_grid_position_grid_penalty_positions AS race_data_starting_grid_position_grid_penalty_positions,
        rd.starting_grid_position_time_millis AS race_data_starting_grid_position_time_millis,
        rd.race_shared_car AS race_data_race_shared_car,
        rd.race_laps AS race_data_race_laps,
        rd.race_time_millis AS race_data_race_time_millis,
        rd.race_time_penalty_millis AS race_data_race_time_penalty_millis,
        rd.race_gap_millis AS race_data_race_gap_millis,
        rd.race_gap_laps AS race_data_race_gap_laps,
        rd.race_interval_millis AS race_data_race_interval_millis,
        rd.race_reason_retired AS race_data_race_reason_retired,
        rd.race_points AS race_data_race_points,
        rd.race_pole_position AS race_data_race_pole_position,
        rd.race_qualification_position_number AS race_data_race_qualification_position_number,
        rd.race_qualification_position_text AS race_data_race_qualification_position_text,
        rd.race_grid_position_number AS race_data_race_grid_position_number,
        rd.race_grid_position_text AS race_data_race_grid_position_text,
        rd.race_positions_gained AS race_data_race_positions_gained,
        rd.race_pit_stops AS race_data_race_pit_stops,
        rd.race_fastest_lap AS race_data_race_fastest_lap,
        rd.race_driver_of_the_day AS race_data_race_driver_of_the_day,
        rd.race_grand_slam AS race_data_race_grand_slam,
        rd.fastest_lap_lap AS race_data_fastest_lap_lap,
        rd.fastest_lap_time_millis AS race_data_fastest_lap_time_millis,
        rd.fastest_lap_gap_millis AS race_data_fastest_lap_gap_millis,
        rd.fastest_lap_interval_millis AS race_data_fastest_lap_interval_millis,
        rd.pit_stop_stop AS race_data_pit_stop_stop,
        rd.pit_stop_lap AS race_data_pit_stop_lap,
        rd.pit_stop_time_millis AS race_data_pit_stop_time_millis,
        rd.driver_of_the_day_percentage AS race_data_driver_of_the_day_percentage,
        CONVERT(
            VARCHAR(96),
            HASHBYTES(
            'MD5',
            CONCAT_WS(
                '|',
                ri.race_id,
                rd.type,
                rd.position_display_order,
                rd.position_number,
                rd.position_text,
                rd.driver_number,
                di.driver_id,
                ci.constructor_id,
                ei.engine_manufacturer_id,
                ti.tyre_manufacturer_id,
                rd.practice_time_millis,
                rd.practice_gap_millis,
                rd.practice_interval_millis,
                rd.practice_laps,
                rd.qualifying_time_millis,
                rd.qualifying_q1_millis,
                rd.qualifying_q2_millis,
                rd.qualifying_q3_millis,
                rd.qualifying_gap_millis,
                rd.qualifying_interval_millis,
                rd.qualifying_laps,
                rd.starting_grid_position_qualification_position_number,
                rd.starting_grid_position_qualification_position_text,
                rd.starting_grid_position_grid_penalty,
                rd.starting_grid_position_grid_penalty_positions,
                rd.starting_grid_position_time_millis,
                rd.race_shared_car,
                rd.race_laps,
                rd.race_time_millis,
                rd.race_time_penalty_millis,
                rd.race_gap_millis,
                rd.race_gap_laps,
                rd.race_interval_millis,
                rd.race_reason_retired,
                rd.race_points,
                rd.race_pole_position,
                rd.race_qualification_position_number,
                rd.race_qualification_position_text,
                rd.race_grid_position_number,
                rd.race_grid_position_text,
                rd.race_positions_gained,
                rd.race_pit_stops,
                rd.race_fastest_lap,
                rd.race_driver_of_the_day,
                rd.race_grand_slam,
                rd.fastest_lap_lap,
                rd.fastest_lap_time_millis,
                rd.fastest_lap_gap_millis,
                rd.fastest_lap_interval_millis,
                rd.pit_stop_stop,
                rd.pit_stop_lap,
                rd.pit_stop_time_millis,
                rd.driver_of_the_day_percentage
            )
            ),
            2
        ) AS dwh_hash,
        COALESCE(
            rd.dwh_valid_to,
            ri.dwh_valid_to,
            di.dwh_valid_to,
            ci.dwh_valid_to,
            ei.dwh_valid_to,
            ti.dwh_valid_to
        ) AS dwh_valid_to
	INTO #src__LoadFactRaceData
	FROM f1db.race_data rd
    JOIN #race_info__LoadFactRaceData ri ON ri.id = rd.race_id
    JOIN #driver_info__LoadFactRaceData di ON di.id = rd.driver_id
    JOIN #constructor_info__LoadFactRaceData ci ON ci.id = rd.constructor_id
    JOIN #engine_info__LoadFactRaceData ei ON ei.id = rd.engine_manufacturer_id
    JOIN #tyre_info__LoadFactRaceData ti ON ti.id = rd.tyre_manufacturer_id
	WHERE GREATEST(
        rd.dwh_modified_at,
        ri.dwh_modified_at,
        di.dwh_modified_at,
        ci.dwh_modified_at,
        ei.dwh_modified_at,
        ti.dwh_modified_at
	) > DATEADD(MINUTE, -5, @left_margin);

 	-- create index on tmp table
	CREATE INDEX idx__src__LoadFactRaceData ON #src__LoadFactRaceData(race_id, race_data_type, race_data_position_display_order);

    -- check if any data has changed even tho it shouldn't have
    IF EXISTS (
        SELECT 1
        FROM #src__LoadFactRaceData src
        INNER JOIN dwh.fact_race_data frd ON frd.race_id = src.race_id AND frd.race_data_type = src.race_data_type AND frd.race_data_position_display_order = src.race_data_position_display_order
        WHERE frd.dwh_hash <> src.dwh_hash
    )
    BEGIN
        THROW 50000, 'dwh_hash has changed for one or more records', 1;
    END;

	-- Merge into the dimension table
    MERGE dwh.fact_race_data AS frd
    USING #src__LoadFactRaceData AS src
    ON frd.race_id = src.race_id AND frd.race_data_type = src.race_data_type AND frd.race_data_position_display_order = src.race_data_position_display_order

	WHEN MATCHED AND (
        src.dwh_valid_to IS NOT NULL AND frd.dwh_valid_to IS NULL
    )
    THEN UPDATE SET
        frd.dwh_modified_at = @now,
        frd.dwh_valid_to = @now

    WHEN NOT MATCHED BY TARGET THEN
    INSERT (
        race_id,
        race_data_type,
        race_data_position_display_order,
        race_data_position_number,
        race_data_position_text,
        race_data_driver_number,
        driver_id,
        constructor_id,
        engine_manufacturer_id,
        tyre_manufacturer_id,
        race_data_practice_time_millis,
        race_data_practice_gap_millis,
        race_data_practice_interval_millis,
        race_data_practice_laps,
        race_data_qualifying_time_millis,
        race_data_qualifying_q1_millis,
        race_data_qualifying_q2_millis,
        race_data_qualifying_q3_millis,
        race_data_qualifying_gap_millis,
        race_data_qualifying_interval_millis,
        race_data_qualifying_laps,
        race_data_starting_grid_position_qualification_position_number,
        race_data_starting_grid_position_qualification_position_text,
        race_data_starting_grid_position_grid_penalty,
        race_data_starting_grid_position_grid_penalty_positions,
        race_data_starting_grid_position_time_millis,
        race_data_race_shared_car,
        race_data_race_laps,
        race_data_race_time_millis,
        race_data_race_time_penalty_millis,
        race_data_race_gap_millis,
        race_data_race_gap_laps,
        race_data_race_interval_millis,
        race_data_race_reason_retired,
        race_data_race_points,
        race_data_race_pole_position,
        race_data_race_qualification_position_number,
        race_data_race_qualification_position_text,
        race_data_race_grid_position_number,
        race_data_race_grid_position_text,
        race_data_race_positions_gained,
        race_data_race_pit_stops,
        race_data_race_fastest_lap,
        race_data_race_driver_of_the_day,
        race_data_race_grand_slam,
        race_data_fastest_lap_lap,
        race_data_fastest_lap_time_millis,
        race_data_fastest_lap_gap_millis,
        race_data_fastest_lap_interval_millis,
        race_data_pit_stop_stop,
        race_data_pit_stop_lap,
        race_data_pit_stop_time_millis,
        race_data_driver_of_the_day_percentage,
        dwh_hash, dwh_valid_from, dwh_modified_at, dwh_valid_to
    )
    VALUES (
        src.race_id,
        src.race_data_type,
        src.race_data_position_display_order,
        src.race_data_position_number,
        src.race_data_position_text,
        src.race_data_driver_number,
        src.driver_id,
        src.constructor_id,
        src.engine_manufacturer_id,
        src.tyre_manufacturer_id,
        src.race_data_practice_time_millis,
        src.race_data_practice_gap_millis,
        src.race_data_practice_interval_millis,
        src.race_data_practice_laps,
        src.race_data_qualifying_time_millis,
        src.race_data_qualifying_q1_millis,
        src.race_data_qualifying_q2_millis,
        src.race_data_qualifying_q3_millis,
        src.race_data_qualifying_gap_millis,
        src.race_data_qualifying_interval_millis,
        src.race_data_qualifying_laps,
        src.race_data_starting_grid_position_qualification_position_number,
        src.race_data_starting_grid_position_qualification_position_text,
        src.race_data_starting_grid_position_grid_penalty,
        src.race_data_starting_grid_position_grid_penalty_positions,
        src.race_data_starting_grid_position_time_millis,
        src.race_data_race_shared_car,
        src.race_data_race_laps,
        src.race_data_race_time_millis,
        src.race_data_race_time_penalty_millis,
        src.race_data_race_gap_millis,
        src.race_data_race_gap_laps,
        src.race_data_race_interval_millis,
        src.race_data_race_reason_retired,
        src.race_data_race_points,
        src.race_data_race_pole_position,
        src.race_data_race_qualification_position_number,
        src.race_data_race_qualification_position_text,
        src.race_data_race_grid_position_number,
        src.race_data_race_grid_position_text,
        src.race_data_race_positions_gained,
        src.race_data_race_pit_stops,
        src.race_data_race_fastest_lap,
        src.race_data_race_driver_of_the_day,
        src.race_data_race_grand_slam,
        src.race_data_fastest_lap_lap,
        src.race_data_fastest_lap_time_millis,
        src.race_data_fastest_lap_gap_millis,
        src.race_data_fastest_lap_interval_millis,
        src.race_data_pit_stop_stop,
        src.race_data_pit_stop_lap,
        src.race_data_pit_stop_time_millis,
        src.race_data_driver_of_the_day_percentage,
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
        @process_name = 'FactRaceData',
        @inserted_count = @inserted_count,
        @updated_count = @updated_count;
    EXEC dwh.SetLeftMargin
        @process_name = 'FactRaceData',
        @last_run_at = @now;

	-- cleanup
    EXEC dwh.LoadFactRaceDataClearTables;
END;
