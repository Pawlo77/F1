-- Test 4: Driver Points Analysis for Early 2025 Season
-- Retrieves total championship points earned by each driver during the first part of 2025 season (January 1 - May 4)
-- Orders results by total points in descending order to show championship standings

SELECT
    d.driver_full_name,
    SUM(frd.race_data_race_points) AS total_points
FROM
    [F1DB].[DWH].[fact_race_data] frd
JOIN
    [F1DB].[DWH].[dim_race] dr ON frd.race_id = dr.dwh_id
JOIN
    [F1DB].[DWH].[dim_driver] d ON frd.driver_id = d.dwh_id
WHERE
    dr.race_date BETWEEN '2025-01-01' AND '2025-05-04'
GROUP BY
    d.driver_full_name
ORDER BY
    total_points DESC;
