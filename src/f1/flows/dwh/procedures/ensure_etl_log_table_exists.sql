/*
  Procedure: dwh.EnsureEtlLogTableExists

  Description:
  This stored procedure ensures that the 'etl_log' table exists in the 'dwh' schema.
  It first checks for the existence of the table using the INFORMATION_SCHEMA.TABLES view.
  If the table does not exist, it creates the table with the following columns:
    - id: A primary key with an auto-incrementing integer value.
    - process_name: A string (NVARCHAR(128)) that stores the name of the ETL process.
    - inserted_count: An integer representing the number of records inserted.
    - updated_count: An integer representing the number of records updated.
    - executed_at: A datetime field that logs the time of execution, defaulting to the current date and time.
*/

CREATE OR ALTER PROCEDURE dwh.EnsureEtlLogTableExists
AS
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'dwh' AND TABLE_NAME = 'etl_log'
  )
  BEGIN
    CREATE TABLE dwh.etl_log (
      id INT IDENTITY(1,1) PRIMARY KEY,
      process_name NVARCHAR(128),
      inserted_count INT,
      updated_count INT,
      executed_at DATETIME DEFAULT GETDATE()
    );
  END;
END;
