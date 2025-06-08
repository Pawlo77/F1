SELECT 
    d.driver_full_name,
    COUNT(*) AS driver_of_the_day_count
FROM 
    [F1DB].[DWH].[fact_race_data] frd
JOIN 
    [F1DB].[DWH].[dim_race] dr ON frd.race_id = dr.dwh_id
JOIN 
    [F1DB].[DWH].[dim_driver] d ON frd.driver_id = d.dwh_id
WHERE 
    YEAR(dr.race_date) = 2025
    AND frd.race_data_race_driver_of_the_day = 1
GROUP BY 
    d.driver_full_name
ORDER BY 
    driver_of_the_day_count DESC;
