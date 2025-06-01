CREATE OR ALTER PROCEDURE dwh.LoadDimCountryClearTables
AS
BEGIN
	DROP TABLE IF EXISTS #src__LoadDimCountry;
END;
