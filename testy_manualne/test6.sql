SELECT 
    DISTINCT c.circuit_name,
    c.circuit_place_name,
    c.circuit_length,
    c.circuit_rating,
    c.circuit_website
FROM 
    [F1DB].[DWH].[dim_race] r
JOIN 
    [F1DB].[DWH].[dim_circuit] c ON r.circuit_id = c.dwh_id
WHERE 
    YEAR(r.race_date) = 2025
ORDER BY 
    c.circuit_name;
