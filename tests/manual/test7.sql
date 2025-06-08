-- Test 7: Race Attendance Statistics for 2025
-- Calculates total number of races, sum of attendance, and average attendance
-- for the 2025 season, excluding races with null attendance values

SELECT
    COUNT(*) AS liczba_wyscigow,
    SUM(r.race_weekend_attendance) AS suma_ogladalnosci,
    AVG(CAST(r.race_weekend_attendance AS FLOAT)) AS srednia_ogladalnosc
FROM
    [F1DB].[DWH].[dim_race] r
WHERE
    YEAR(r.race_date) = 2025
    AND r.race_weekend_attendance IS NOT NULL;
