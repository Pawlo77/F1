-- Test 2: Constructor Championship Standings for 2025
-- Retrieves total points earned by each constructor during the 2025 season
-- Results are ordered by total points in descending order to show championship standings

SELECT
    c.constructor_name,
    SUM(frd.race_data_race_points) AS total_points
FROM
    [F1DB].[DWH].[fact_race_data] frd
JOIN
    [F1DB].[DWH].[dim_race] dr ON frd.race_id = dr.dwh_id
JOIN
    [F1DB].[DWH].[dim_constructor] c ON frd.constructor_id = c.dwh_id
WHERE
    YEAR(dr.race_date) = 2025
GROUP BY
    c.constructor_name
ORDER BY
    total_points DESC;
