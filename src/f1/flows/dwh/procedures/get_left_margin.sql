/*
  PROCEDURE: dwh.GetLeftMargin

  DESCRIPTION:
    Retrieves the left margin datetime value for a specified process by selecting the maximum last_run_at
    from the dwh.configuration table. If there are no records for the given process, a default value of
    '1900-01-01' is returned. Prior to executing the SELECT, the procedure ensures the configuration table
    exists by calling dwh.EnsureConfigurationTableExists.

  PARAMETERS:
    @process_name NVARCHAR(128)
      The identifier for the process whose left margin is being calculated.

    @left_margin DATETIME OUTPUT
      An output parameter that returns the calculated left margin datetime.

  NOTES:
    - SET NOCOUNT ON is used to suppress extra result sets.
    - The default '1900-01-01' value ensures a consistent starting point when no previous run datetime exists.
*/

CREATE OR ALTER PROCEDURE dwh.GetLeftMargin
  @process_name NVARCHAR(128),
  @left_margin DATETIME OUTPUT
AS
BEGIN
  SET NOCOUNT ON;

 	EXEC dwh.EnsureConfigurationTableExists;

  -- Get left_margin
  SELECT @left_margin = COALESCE(MAX(last_run_at), '1900-01-01')
  FROM dwh.configuration
  WHERE process_name = @process_name;
END;
