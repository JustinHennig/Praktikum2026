-- Sample measurement settings: oscilloscope sweep on channel 1
INSERT INTO measurement_settings (device, configuration) VALUES (
    'USB0::0xF4EC::0x1011::SDS5ADED4R0001::INSTR',
    '{"channel": 1, "v_div_mv": 500, "t_div_ms": 1.0, "offset_mv": 0.0, "trigger_level": 0.5}'
);

-- Sample measurement settings: oscilloscope sweep on channel 2
INSERT INTO measurement_settings (device, configuration) VALUES (
    'USB0::0xF4EC::0x1011::SDS5ADED4R0001::INSTR',
    '{"channel": 2, "v_div_mv": 200, "t_div_ms": 0.5, "offset_mv": 0.0, "trigger_level": 0.3}'
);

-- Sample measurements for measurement_id 1
INSERT INTO measurements (measurement_id, time, measurement_values) VALUES (1, '2026-03-20 09:00:00', '{"Frequency": "1000.00", "Amplitude": "3.30",  "Peak-to-Peak": "6.60",  "RMS": "2.33"}');
INSERT INTO measurements (measurement_id, time, measurement_values) VALUES (1, '2026-03-20 09:00:01', '{"Frequency": "1000.12", "Amplitude": "3.28", "Peak-to-Peak": "6.56",  "RMS": "2.31"}');
INSERT INTO measurements (measurement_id, time, measurement_values) VALUES (1, '2026-03-20 09:00:02', '{"Frequency": "999.87",  "Amplitude": "3.31", "Peak-to-Peak": "6.62",  "RMS": "2.34"}');
INSERT INTO measurements (measurement_id, time, measurement_values) VALUES (1, '2026-03-20 09:00:03', '{"Frequency": "1000.05", "Amplitude": "3.29", "Peak-to-Peak": "6.58",  "RMS": "2.32"}');
INSERT INTO measurements (measurement_id, time, measurement_values) VALUES (1, '2026-03-20 09:00:04', '{"Frequency": "1000.23", "Amplitude": "3.32", "Peak-to-Peak": "6.64",  "RMS": "2.35"}');

-- Sample measurements for measurement_id 2
INSERT INTO measurements (measurement_id, time, measurement_values) VALUES (2, '2026-03-20 10:00:00', '{"Frequency": "500.00", "Amplitude": "1.80",  "Peak-to-Peak": "3.60",  "RMS": "1.27"}');
INSERT INTO measurements (measurement_id, time, measurement_values) VALUES (2, '2026-03-20 10:00:01', '{"Frequency": "499.95", "Amplitude": "1.79",  "Peak-to-Peak": "3.58",  "RMS": "1.26"}');
INSERT INTO measurements (measurement_id, time, measurement_values) VALUES (2, '2026-03-20 10:00:02', '{"Frequency": "500.08", "Amplitude": "1.81",  "Peak-to-Peak": "3.62",  "RMS": "1.28"}');

-- Sample measurement settings: function generator channel 1
INSERT INTO measurement_settings (device, configuration) VALUES (
    'USB0::0xF4EC::0x1102::SDG6EBAD4Q0001::INSTR',
    '{"channel": 1}'
);

-- Sample measurements for measurement_id 3 (function generator)
INSERT INTO measurements (measurement_id, time, measurement_values) VALUES (3, '2026-03-20 11:00:00', '{"Waveform": "SINE",   "Frequency": "1000.00", "Amplitude": "3.30", "Offset": "0.00", "Phase": "0.00"}');
INSERT INTO measurements (measurement_id, time, measurement_values) VALUES (3, '2026-03-20 11:00:05', '{"Waveform": "SINE",   "Frequency": "2000.00", "Amplitude": "3.30", "Offset": "0.00", "Phase": "0.00"}');
INSERT INTO measurements (measurement_id, time, measurement_values) VALUES (3, '2026-03-20 11:00:10', '{"Waveform": "SQUARE", "Frequency": "2000.00", "Amplitude": "2.50", "Offset": "0.50", "Phase": "0.00"}');
INSERT INTO measurements (measurement_id, time, measurement_values) VALUES (3, '2026-03-20 11:00:15', '{"Waveform": "SQUARE", "Frequency": "5000.00", "Amplitude": "2.50", "Offset": "0.50", "Phase": "45.00"}');
