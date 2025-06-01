/*
Docstring: dwh.SetLeftMargin Stored Procedure

Purpose:
  Updates the last_run_at configuration for a given process name by performing an upsert operation on the dwh.configuration table.
  Prior to the upsert, it ensures that the configuration table exists by calling dwh.EnsureConfigurationTableExists.

Parameters:
  @process_name NVARCHAR(128)
    - Specifies the unique name of the process whose configuration is being set.

  @last_run_at DATETIME
    - Represents the datetime for when the process was last run.

Operation:
  - Checks if dwh.configuration has an entry for the provided process_name.
  - If the entry exists, updates the last_run_at value.
  - If the entry does not exist, inserts a new record with the provided process_name and last_run_at.

Usage Example:
  EXEC dwh.SetLeftMargin @process_name = 'ProcessA', @last_run_at = GETDATE();

Remarks:
  Ensure that the dwh.EnsureConfigurationTableExists procedure is operational before using this stored procedure.
*/

CREATE OR ALTER PROCEDURE dwh.SetLeftMargin
  @process_name NVARCHAR(128),
  @last_run_at DATETIME
AS
BEGIN
  SET NOCOUNT ON;

	EXEC dwh.EnsureConfigurationTableExists;

  -- Upsert the configuration
  MERGE dwh.configuration AS target
  USING (SELECT @process_name AS process_name, @last_run_at AS last_run_at) AS src
  ON target.process_name = src.process_name
  WHEN MATCHED THEN
    UPDATE SET last_run_at = src.last_run_at
  WHEN NOT MATCHED THEN
    INSERT (process_name, last_run_at) VALUES (src.process_name, src.last_run_at);
END;
