SELECT 
    d.driver_full_name,
    c.country_name,
    d.driver_date_of_birth,
    COUNT(CASE 
        WHEN frd.race_data_position_number = 1 AND frd.race_data_type = 'RACE_RESULT' THEN 1 
    END) AS race_wins,
    COUNT(CASE 
        WHEN frd.race_data_position_number IN (1, 2, 3) AND frd.race_data_type = 'RACE_RESULT' THEN 1 
    END) AS podiums,
    SUM(CASE 
        WHEN frd.race_data_type = 'RACE_RESULT' THEN frd.race_data_race_points 
        ELSE 0 
    END) AS total_race_points
FROM 
    [F1DB].[DWH].[fact_race_data] frd
JOIN 
    [F1DB].[DWH].[dim_driver] d ON frd.driver_id = d.dwh_id
JOIN 
    [F1DB].[DWH].[dim_country] c ON d.driver_nationality_country_id = c.dwh_id
WHERE 
    d.driver_name = 'Robert Kubica'
GROUP BY 
    d.driver_full_name, c.country_name, d.driver_date_of_birth;
