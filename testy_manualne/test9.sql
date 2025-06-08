DECLARE @today DATE = CAST(GETDATE() AS DATE);

SELECT TOP 1
    r.race_date,
    r.race_grand_prix_name,
    c.circuit_name,
    c.circuit_place_name
FROM
    [F1DB].[DWH].[dim_race] r
JOIN
    [F1DB].[DWH].[dim_circuit] c ON r.circuit_id = c.dwh_id
WHERE
    r.race_date >= @today
ORDER BY
    r.race_date ASC;
