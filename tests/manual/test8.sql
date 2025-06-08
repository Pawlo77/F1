-- Test 8: Race Status Analysis for 2025
-- Counts completed and upcoming races for the 2025 season based on current date
-- Provides overview of season progress by comparing race dates to today's date

DECLARE @today DATE = CAST(GETDATE() AS DATE);

SELECT
    COUNT(CASE WHEN r.race_date <= @today THEN 1 END) AS liczba_ukonczonych_wyscigow,
    COUNT(CASE WHEN r.race_date > @today THEN 1 END) AS liczba_nadchodzacych_wyscigow
FROM
    [F1DB].[DWH].[dim_race] r
WHERE
    YEAR(r.race_date) = 2025;
