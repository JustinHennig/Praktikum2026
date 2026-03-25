-- Drops all application tables and resets their AUTOINCREMENT counters.
-- Child table must be dropped before the parent to satisfy foreign key constraints.

DROP TABLE IF EXISTS measurements;
DROP TABLE IF EXISTS measurement_settings;

-- Remove AUTOINCREMENT counters so IDs start from 1 when tables are recreated
DELETE FROM sqlite_sequence WHERE name IN ('measurements', 'measurement_settings');