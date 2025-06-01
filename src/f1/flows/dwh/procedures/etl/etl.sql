/*
    Procedure: dwh.etl
    Description: This stored procedure orchestrates the overall ETL process by sequentially executing the procedures
                 dwh.LoadAllDimData and dwh.LoadAllFactData to load dimension and fact data into the data warehouse.

    Workflow:
        - Sets NOCOUNT ON to minimize unnecessary messaging.
        - Drops the temporary table (#res__Etl) if it exists.
        - Creates a temporary table (#res__Etl) to capture the output from the ETL operations.
        - Executes dwh.LoadAllDimData and inserts its result (including procedure name, inserted rows count, and updated rows count) into the temporary table.
        - Executes dwh.LoadAllFactData and appends its result to the temporary table.
        - Selects and returns all rows from the temporary table to consolidate the ETL operation results.

    Usage:
        EXEC dwh.etl;

    Requirements:
        - Both dwh.LoadAllDimData and dwh.LoadAllFactData must be defined and accessible.
        - Each underlying procedure should return a result set containing the procedure name along with counts of inserted and updated rows.
*/
CREATE OR ALTER PROCEDURE dwh.etl AS
BEGIN
    SET NOCOUNT ON;

    DROP TABLE IF EXISTS #res__Etl;

    -- Temporary table to hold the results
    CREATE TABLE #res__Etl (
        procedure_name NVARCHAR(100),
        inserted_rows INT,
        updated_rows INT
    );

    INSERT INTO #res__Etl
    EXEC dwh.LoadAllDimData;

    INSERT INTO #res__Etl
    EXEC dwh.LoadAllFactData;

    SELECT * FROM #res__Etl;
END;
