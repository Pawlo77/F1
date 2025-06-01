CREATE OR ALTER PROCEDURE dwh.LoadFactRaceDataClearTables
AS
BEGIN
	DROP TABLE IF EXISTS
		#driver_info__LoadFactRaceData,
		#constructor_info__LoadFactRaceData,
		#engine_info__LoadFactRaceData,
		#tyre_info__LoadFactRaceData,
		#race_info__LoadFactRaceData,
		#src__LoadFactRaceData;
END;
