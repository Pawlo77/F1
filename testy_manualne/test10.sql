DECLARE @today DATE = CAST(GETDATE() AS DATE);

DECLARE @last_race_id INT = (
    SELECT TOP 1 dwh_id
    FROM [F1DB].[DWH].[dim_race]
    WHERE race_date <= @today
    ORDER BY race_date DESC
);

SELECT 
    d.driver_full_name,
    frd.race_data_race_time_millis,
    frd.race_data_race_points,
    FORMAT(DATEADD(MILLISECOND, frd.race_data_race_time_millis, 0), 'HH:mm:ss') AS formatted_race_time
FROM 
    [F1DB].[DWH].[fact_race_data] frd
JOIN 
    [F1DB].[DWH].[dim_driver] d ON frd.driver_id = d.dwh_id
WHERE 
    frd.race_id = @last_race_id
    AND frd.race_data_type = 'RACE_RESULT'
ORDER BY 
    frd.race_data_position_number ASC;
