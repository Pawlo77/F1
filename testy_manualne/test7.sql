SELECT 
    COUNT(*) AS liczba_wyscigow,
    SUM(r.race_weekend_attendance) AS suma_ogladalnosci,
    AVG(CAST(r.race_weekend_attendance AS FLOAT)) AS srednia_ogladalnosc
FROM 
    [F1DB].[DWH].[dim_race] r
WHERE 
    YEAR(r.race_date) = 2025
    AND r.race_weekend_attendance IS NOT NULL;
