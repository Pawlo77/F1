/*
Procedure: dwh.EnsureConfigurationTableExists
Description:
  Checks if the "configuration" table exists in the "dwh" schema.
  If the table does not exist, it creates the table with the following structure:
    - process_name: NVARCHAR(128), serves as the primary key.
    - last_run_at: DATETIME, intended to store the timestamp of the last execution/run.
Usage:
  EXEC dwh.EnsureConfigurationTableExists;
Notes:
  - Relies on INFORMATION_SCHEMA.TABLES to verify existence of the table.
  - Ensures that the table is available for subsequent operations that depend on configuration data.
*/

CREATE OR ALTER PROCEDURE dwh.EnsureConfigurationTableExists
AS
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'dwh' AND TABLE_NAME = 'configuration'
  )
  BEGIN
    CREATE TABLE dwh.configuration (
      process_name NVARCHAR(128) PRIMARY KEY,
      last_run_at DATETIME
    );
  END;
END;
