/*
    Procedure: dwh.LoadAllDimData
    Description: This stored procedure performs the ETL process for loading dimension data into the data warehouse.

    Workflow:
        - Drops any pre-existing temporary results table (#res__LoadAllDimData).
        - Creates a temporary table to capture the results from each individual dimension loading procedure.
        - Sequentially calls various dimension loaders (e.g., f1db.LoadDimCountry, f1db.LoadDimConstructor, etc.),
            each returning the count of inserted and updated rows.
        - Records the output results (procedure name, inserted rows count, updated rows count) in the temporary table.
        - Finally, selects the contents of the temporary table to return the aggregated results.

    Usage:
        EXEC dwh.LoadAllDimData;

    Requirements:
        - The individual dimension loading procedures (e.g., LoadDimCountry, LoadDimConstructor, etc.)
            must exist and be accessible in the referenced schema (f1db).
*/
CREATE OR ALTER PROCEDURE dwh.LoadAllDimData
AS
BEGIN
  SET NOCOUNT ON;

  DROP TABLE IF EXISTS #res__LoadAllDimData;

  -- Temporary table to hold the results
  CREATE TABLE #res__LoadAllDimData
  (
    procedure_name NVARCHAR(100),
    inserted_rows INT,
    updated_rows INT
  );

  DECLARE @ins INT, @upd INT;

  -- Call f1db.LoadDimCountry
  SET @ins = 0; SET @upd = 0;
  EXEC f1db.LoadDimCountry @inserted_count = @ins OUTPUT, @updated_count = @upd OUTPUT;
  INSERT INTO #res__LoadAllDimData (procedure_name, inserted_rows, updated_rows)
    VALUES ('LoadDimCountry', @ins, @upd);

  -- Call f1db.LoadDimConstructor
  SET @ins = 0; SET @upd = 0;
  EXEC f1db.LoadDimConstructor @inserted_count = @ins OUTPUT, @updated_count = @upd OUTPUT;
  INSERT INTO #res__LoadAllDimData (procedure_name, inserted_rows, updated_rows)
    VALUES ('LoadDimConstructor', @ins, @upd);

  -- Call f1db.LoadDimDriver
  SET @ins = 0; SET @upd = 0;
  EXEC f1db.LoadDimDriver @inserted_count = @ins OUTPUT, @updated_count = @upd OUTPUT;
  INSERT INTO #res__LoadAllDimData (procedure_name, inserted_rows, updated_rows)
    VALUES ('LoadDimDriver', @ins, @upd);

  -- Call f1db.LoadDimEngineManufacturer
  SET @ins = 0; SET @upd = 0;
  EXEC f1db.LoadDimEngineManufacturer @inserted_count = @ins OUTPUT, @updated_count = @upd OUTPUT;
  INSERT INTO #res__LoadAllDimData (procedure_name, inserted_rows, updated_rows)
    VALUES ('LoadDimEngineManufacturer', @ins, @upd);

  -- Call f1db.LoadDimTyreManufacturer
  SET @ins = 0; SET @upd = 0;
  EXEC f1db.LoadDimTyreManufacturer @inserted_count = @ins OUTPUT, @updated_count = @upd OUTPUT;
  INSERT INTO #res__LoadAllDimData (procedure_name, inserted_rows, updated_rows)
    VALUES ('LoadDimTyreManufacturer', @ins, @upd);

  -- Call f1db.LoadDimCircuit
  SET @ins = 0; SET @upd = 0;
  EXEC f1db.LoadDimCircuit @inserted_count = @ins OUTPUT, @updated_count = @upd OUTPUT;
  INSERT INTO #res__LoadAllDimData (procedure_name, inserted_rows, updated_rows)
    VALUES ('LoadDimCircuit', @ins, @upd);

  -- Call f1db.LoadDimRace
  SET @ins = 0; SET @upd = 0;
  EXEC f1db.LoadDimRace @inserted_count = @ins OUTPUT, @updated_count = @upd OUTPUT;
  INSERT INTO #res__LoadAllDimData (procedure_name, inserted_rows, updated_rows)
    VALUES ('LoadDimRace', @ins, @upd);

  -- Return the results table
  SELECT procedure_name, inserted_rows, updated_rows
  FROM #res__LoadAllDimData;
END;
