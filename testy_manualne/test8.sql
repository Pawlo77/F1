DECLARE @today DATE = CAST(GETDATE() AS DATE);

SELECT 
    COUNT(CASE WHEN r.race_date <= @today THEN 1 END) AS liczba_ukonczonych_wyscigow,
    COUNT(CASE WHEN r.race_date > @today THEN 1 END) AS liczba_nadchodzacych_wyscigow
FROM 
    [F1DB].[DWH].[dim_race] r
WHERE 
    YEAR(r.race_date) = 2025;
