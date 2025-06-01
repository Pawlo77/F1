CREATE OR ALTER PROCEDURE dwh.LoadDimConstructorClearTables
AS
BEGIN
	DROP TABLE IF EXISTS #src__LoadDimConstructor;
END;
