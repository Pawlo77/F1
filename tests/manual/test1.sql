-- Test 1: Driver Points Summary for 2025 Season
-- Retrieves total championship points earned by each driver during the 2025 racing season
-- Results are ordered by total points in descending order (highest scorer first)
-- Uses fact table joined with driver and race dimensions to aggregate point totals

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
    YEAR(dr.race_date) = 2025
GROUP BY
    d.driver_full_name
ORDER BY
    total_points DESC;
