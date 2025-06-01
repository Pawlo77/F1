CREATE OR ALTER PROCEDURE dwh.LoadDimEngineManufacturerClearTables
AS
BEGIN
	DROP TABLE IF EXISTS #src__LoadDimEngineManufacturer;
END;
