CREATE TABLE IF NOT EXISTS measurement_settings (
    measurement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    device TEXT NOT NULL,
    configuration TEXT NOT NULL  -- JSON to save the configuration settings
);

CREATE TABLE IF NOT EXISTS measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    measurement_id INTEGER NOT NULL,
    time TEXT NOT NULL,
    measurement_values TEXT NOT NULL, -- JSON to save the measurement values
    FOREIGN KEY (measurement_id) REFERENCES measurement_settings(measurement_id)
);