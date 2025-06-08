-- Test 11: Ferrari Latest Year Engine and Chassis Configuration
-- Retrieves Ferrari's engine and chassis details for their most recent year of participation
-- Shows engine configuration, full engine name, and chassis name for the latest entrant year

DECLARE @ferrari_id INT = (
    SELECT dwh_id
    FROM [F1DB].[DWH].[dim_constructor]
    WHERE constructor_name = 'Ferrari'
);

DECLARE @last_year INT = (
    SELECT MAX(entrant_year)
    FROM [F1DB].[DWH].[fact_entrant]
    WHERE constructor_id = @ferrari_id
);

SELECT DISTINCT
    entrant_engine_full_name AS engine_name,
    entrant_chassis_full_name AS chassis_name,
	entrant_engine_configuration AS engine_configuration,
    entrant_year
FROM
    [F1DB].[DWH].[fact_entrant]
WHERE
    constructor_id = @ferrari_id
    AND entrant_year = @last_year;
