CREATE OR ALTER PROCEDURE f1db.LoadFactEntrant
    @inserted_count INT OUTPUT,
    @updated_count INT OUTPUT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @now DATETIME = GETDATE();
    DECLARE @merge_output TABLE (action_type NVARCHAR(10));
    DECLARE @left_margin DATETIME;

    -- Get left_margin
    EXEC dwh.GetLeftMargin @process_name = 'FactEntrant', @left_margin = @left_margin OUTPUT;

	-- Prepare temporary table
	EXEC dwh.LoadFactRaceDataClearTables;

	-- main select
	SELECT
        -- base
        e.id AS entrant_id,
        e.name AS entrant_name,
        se.year AS entrant_year,
        -- country
        dco.dwh_id AS country_id,
        -- constructor
        dc.dwh_id AS constructor_id,
        -- engine manufacturer
        dem.dwh_id AS engine_manufacturer_id,
        -- engine
        eg.name AS entrant_engine_name,
        eg.full_name AS entrant_engine_full_name,
        eg.capacity AS entrant_engine_capacity,
        eg.configuration AS entrant_engine_configuration,
        eg.aspiration AS entrant_engine_aspiration,
        -- tyre manufacturer
        dtm.dwh_id AS tyre_manufacturer_id,
        -- chasis
        ch.name AS entrant_chassis_name,
        ch.full_name AS entrant_chassis_full_name,
        -- driver
        ddr.dwh_id AS driver_id,
        sed.rounds AS entrant_driver_rounds,
        sed.rounds_text AS entrant_driver_rounds_text,
        sed.test_driver AS entrant_test_driver,
        -- dwh
        CONVERT(
            VARCHAR(96),
            HASHBYTES('MD5',
            CONCAT_WS('|',
                e.id,
                e.name,
                se.year,
                dco.dwh_id,
                dc.dwh_id,
                dem.dwh_id,
                eg.name,
                eg.full_name,
                eg.capacity,
                eg.configuration,
                eg.aspiration,
                dtm.dwh_id,
                ch.name,
                ch.full_name,
                ddr.dwh_id,
                sed.rounds,
                sed.rounds_text,
                sed.test_driver
                )
            ),
            2
        ) AS dwh_hash,
        COALESCE(
            e.dwh_valid_to,
            se.dwh_valid_to,
            c.dwh_valid_to,
            sec.dwh_valid_to,
            ct.dwh_valid_to,
            em.dwh_valid_to,
            see.dwh_valid_to,
            eg.dwh_valid_to,
            setm.dwh_valid_to,
            tm.dwh_valid_to,
            sech.dwh_valid_to,
            ch.dwh_valid_to,
            sed.dwh_valid_to,
            dr.dwh_valid_to
        ) AS dwh_valid_to
    INTO #src__LoadFactEntrant
    -- base
    FROM f1db.entrant e
    JOIN f1db.season_entrant se
        ON se.entrant_id = e.id
    -- country
    JOIN f1db.country c
        ON c.id = se.country_id
    JOIN dwh.dim_country dco
        ON c.name = dco.country_name
    -- constructor
    JOIN f1db.season_entrant_constructor sec
        ON sec.entrant_id = e.id
        AND sec.year = se.year
    JOIN f1db.constructor ct
        ON sec.constructor_id = ct.id
    JOIN dwh.dim_constructor dc
        ON ct.name = dc.constructor_name
        AND ct.full_name = dc.constructor_full_name
    -- engine manufacturer
    JOIN f1db.engine_manufacturer em
        ON sec.engine_manufacturer_id = em.id
    JOIN dwh.dim_engine_manufacturer dem
        ON em.name = dem.engine_name
    -- engine
    JOIN f1db.season_entrant_engine see
        ON see.entrant_id = e.id
        AND see.year = se.year
        AND see.constructor_id = sec.constructor_id
        AND see.engine_manufacturer_id = sec.engine_manufacturer_id
    JOIN f1db.engine eg
        ON see.engine_id = eg.id
    -- tyre manufacturer
    JOIN f1db.season_entrant_tyre_manufacturer setm
        ON setm.entrant_id = e.id
        AND setm.year = se.year
        AND setm.constructor_id = sec.constructor_id
        AND setm.engine_manufacturer_id = sec.engine_manufacturer_id
    JOIN f1db.tyre_manufacturer tm
        ON setm.tyre_manufacturer_id = tm.id
    JOIN dwh.dim_tyre_manufacturer dtm
        ON dtm.tyre_manufacturer_name = tm.name
    -- chasis
    JOIN f1db.season_entrant_chassis sech
        ON sech.entrant_id = e.id
        AND sech.year = se.year
        AND sech.constructor_id = sec.constructor_id
        AND sech.engine_manufacturer_id = sec.engine_manufacturer_id
    JOIN f1db.chassis ch
        ON ch.id = sech.chassis_id
    -- driver
    JOIN f1db.season_entrant_driver sed
        ON sed.entrant_id = e.id
        AND sed.year = se.year
        AND sed.constructor_id = sec.constructor_id
        AND sed.engine_manufacturer_id = sec.engine_manufacturer_id
    JOIN f1db.driver dr
        ON sed.driver_id = dr.id
    JOIN dwh.dim_driver ddr
        ON ddr.driver_full_name = dr.full_name
        AND ddr.driver_date_of_birth = dr.date_of_birth
	WHERE GREATEST(
        e.dwh_modified_at,
		se.dwh_modified_at,
		c.dwh_modified_at,
		sec.dwh_modified_at,
		ct.dwh_modified_at,
		em.dwh_modified_at,
		see.dwh_modified_at,
		eg.dwh_modified_at,
		setm.dwh_modified_at,
		tm.dwh_modified_at,
		sech.dwh_modified_at,
		ch.dwh_modified_at,
		sed.dwh_modified_at,
		dr.dwh_modified_at
	) > DATEADD(MINUTE, -5, @left_margin);

    -- create index on tmp table
	CREATE INDEX idx__src__LoadFactEntrant ON #src__LoadFactEntrant(
        entrant_name,
        entrant_year,
        constructor_id,
        engine_manufacturer_id,
        entrant_engine_full_name,
        tyre_manufacturer_id,
        entrant_chassis_full_name,
        driver_id
    );

    -- check if any data has changed even tho it shouldn't have
    IF EXISTS (
        SELECT 1
        FROM #src__LoadFactEntrant src
        INNER JOIN dwh.fact_entrant fe
            ON src.entrant_name = fe.entrant_name AND
                src.entrant_year = fe.entrant_year AND
                src.constructor_id = fe.constructor_id AND
                src.engine_manufacturer_id = fe.engine_manufacturer_id AND
                src.entrant_engine_full_name = fe.entrant_engine_full_name AND
                src.tyre_manufacturer_id = fe.tyre_manufacturer_id AND
                src.entrant_chassis_full_name = fe.entrant_chassis_full_name AND
                src.driver_id = fe.driver_id
        WHERE fe.dwh_hash <> src.dwh_hash
    )
    BEGIN
        THROW 50000, 'dwh_hash has changed for one or more records', 1;
    END;

	-- Merge into the dimension table
    MERGE dwh.fact_entrant AS fe
    USING #src__LoadFactEntrant AS src
        ON src.entrant_name = fe.entrant_name AND
            src.entrant_year = fe.entrant_year AND
            src.constructor_id = fe.constructor_id AND
            src.engine_manufacturer_id = fe.engine_manufacturer_id AND
            src.entrant_engine_full_name = fe.entrant_engine_full_name AND
            src.tyre_manufacturer_id = fe.tyre_manufacturer_id AND
            src.entrant_chassis_full_name = fe.entrant_chassis_full_name AND
            src.driver_id = fe.driver_id

    WHEN MATCHED AND (
        src.dwh_valid_to IS NOT NULL AND fe.dwh_valid_to IS NULL
    )
    THEN UPDATE SET
        fe.dwh_modified_at = @now,
        fe.dwh_valid_to = @now

    WHEN NOT MATCHED BY TARGET THEN
    INSERT (
        entrant_name,
        entrant_year,
        country_id,
        constructor_id,
        engine_manufacturer_id,
        entrant_engine_name,
        entrant_engine_full_name,
        entrant_engine_capacity,
        entrant_engine_configuration,
        entrant_engine_aspiration,
        tyre_manufacturer_id,
        entrant_chassis_name,
        entrant_chassis_full_name,
        driver_id,
        entrant_driver_rounds,
        entrant_driver_rounds_text,
        entrant_test_driver,
        dwh_hash,
        dwh_valid_from,
        dwh_modified_at,
        dwh_valid_to
    )
    VALUES (
        src.entrant_name,
        src.entrant_year,
        src.country_id,
        src.constructor_id,
        src.engine_manufacturer_id,
        src.entrant_engine_name,
        src.entrant_engine_full_name,
        src.entrant_engine_capacity,
        src.entrant_engine_configuration,
        src.entrant_engine_aspiration,
        src.tyre_manufacturer_id,
        src.entrant_chassis_name,
        src.entrant_chassis_full_name,
        src.driver_id,
        src.entrant_driver_rounds,
        src.entrant_driver_rounds_text,
        src.entrant_test_driver,
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
        @process_name = 'FactEntrant',
        @inserted_count = @inserted_count,
        @updated_count = @updated_count;
	EXEC dwh.SetLeftMargin
        @process_name = 'FactEntrant',
        @last_run_at = @now;

	-- cleanup
	EXEC dwh.LoadFactRaceDataClearTables;
END;
