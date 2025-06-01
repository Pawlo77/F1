CREATE OR ALTER PROCEDURE dwh.LoadFactEntrantClearTables
AS
BEGIN
	DROP TABLE IF EXISTS #src__LoadFactEntrant;
END;
