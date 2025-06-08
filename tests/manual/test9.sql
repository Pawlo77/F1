-- Test 9: Next Upcoming Race Information
-- Retrieves details of the next scheduled F1 race from today's date
-- Returns race date, Grand Prix name, circuit name, and location for the closest future race

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
