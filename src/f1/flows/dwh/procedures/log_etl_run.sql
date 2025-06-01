/*
Procedure: dwh.LogEtlRun
Description:
  Inserts an ETL run record into the dwh.etl_log table after ensuring that the log table exists.
  It logs the process name, counts for inserted and updated records, and the timestamp when the procedure is executed.

Parameters:
  @process_name NVARCHAR(128) - The name of the ETL process.
  @inserted_count INT - The number of records inserted during the ETL process.
  @updated_count INT - The number of records updated during the ETL process.

Usage:
  Call the procedure to log the ETL run details:
    EXEC dwh.LogEtlRun @process_name, @inserted_count, @updated_count;
*/

CREATE OR ALTER PROCEDURE dwh.LogEtlRun
  @process_name NVARCHAR(128),
  @inserted_count INT,
  @updated_count INT
AS
BEGIN
  SET NOCOUNT ON;

 	EXEC dwh.EnsureEtlLogTableExists;

  INSERT INTO dwh.etl_log (
    process_name,
    inserted_count,
    updated_count,
    executed_at
  )
  VALUES (
    @process_name,
    @inserted_count,
    @updated_count,
    GETDATE()
  );
END;
