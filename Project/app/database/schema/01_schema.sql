CREATE TABLE IF NOT EXISTS measurement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    date_time TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS measurement_setting (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    measurement_id INTEGER NOT NULL,
    device TEXT NOT NULL,
    configuration TEXT NOT NULL,  -- JSON to save the configuration settings
    FOREIGN KEY (measurement_id) REFERENCES measurement(id)
);

CREATE TABLE IF NOT EXISTS measurement_value (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    measurement_setting_id INTEGER NOT NULL,
    time TEXT NOT NULL,
    measurement_values TEXT NOT NULL, -- JSON to save the measurement values
    FOREIGN KEY (measurement_setting_id) REFERENCES measurement_setting(id)
);