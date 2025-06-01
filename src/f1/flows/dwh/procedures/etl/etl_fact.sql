/*
    Procedure: dwh.LoadAllFactData
    Description: This stored procedure performs the ETL process for loading fact data into the data warehouse.

    Workflow:
        - Drops any pre-existing temporary results table (#res__LoadAllFactData).
        - Creates a temporary table to capture the results from each individual dimension loading procedure.
        - Sequentially calls various fact loaders (e.g., f1db.LoadFactRaceData, f1db.LoadFactEntrant, etc.),
            each returning the count of inserted and updated rows.
        - Records the output results (procedure name, inserted rows count, updated rows count) in the temporary table.
        - Finally, selects the contents of the temporary table to return the aggregated results.

    Usage:
        EXEC dwh.LoadAllFactData;

    Requirements:
        - The individual facts loading procedures (e.g., LoadFactRaceData, LoadFactEntrant, etc.)
            must exist and be accessible in the referenced schema (f1db).
*/
CREATE OR ALTER PROCEDURE dwh.LoadAllFactData
AS
BEGIN
  SET NOCOUNT ON;

  DROP TABLE IF EXISTS #res__LoadAllFactData;

  -- Temporary table to hold the results
  CREATE TABLE #res__LoadAllFactData
  (
    procedure_name NVARCHAR(100),
    inserted_rows INT,
    updated_rows INT
  );

  DECLARE @ins INT, @upd INT;

  -- Call f1db.LoadFactEntrant
  SET @ins = 0; SET @upd = 0;
  EXEC f1db.LoadFactEntrant @inserted_count = @ins OUTPUT, @updated_count = @upd OUTPUT;
  INSERT INTO #res__LoadAllFactData (procedure_name, inserted_rows, updated_rows)
    VALUES ('LoadFactEntrant', @ins, @upd);

  -- Call f1db.LoadFactRaceData
  SET @ins = 0; SET @upd = 0;
  EXEC f1db.LoadFactRaceData @inserted_count = @ins OUTPUT, @updated_count = @upd OUTPUT;
  INSERT INTO #res__LoadAllFactData (procedure_name, inserted_rows, updated_rows)
    VALUES ('LoadFactRaceData', @ins, @upd);

  -- Return the results table
  SELECT procedure_name, inserted_rows, updated_rows
  FROM #res__LoadAllFactData;
END;
