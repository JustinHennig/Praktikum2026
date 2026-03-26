-- Drops all application tables and resets their AUTOINCREMENT counters.
-- Child tables must be dropped before parent to satisfy foreign key constraints.

DROP TABLE IF EXISTS measurement_value;
DROP TABLE IF EXISTS measurement_setting;
DROP TABLE IF EXISTS measurement;

-- Remove AUTOINCREMENT counters so IDs start from 1 when tables are recreated
DELETE FROM sqlite_sequence WHERE name IN ('measurement_value', 'measurement_setting', 'measurement');