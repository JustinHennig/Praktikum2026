"""
Utility to inject mock measurement data into the MeasurementDisplay table.
Call inject_mock_data(window) after the MainWindow is created.

Usage in main.py:
    from utils.create_data_for_displa import inject_mock_data
    inject_mock_data(window)
"""

import datetime
import random


def _oscilloscope_row(resource: str, channel: int, base_freq: float) -> dict:
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "Resource": resource,
        "Channel": channel,
        "Time": ts,
        "v_div_mv": "500",
        "t_div_ms": "1.0",
        "offset_mv": "0.0",
        "trigger_level": "0.5",
        "Frequency":    f"{base_freq + random.uniform(-0.5, 0.5):.4f}",
        "Amplitude":    f"{3.30 + random.uniform(-0.05, 0.05):.4f}",
        "Peak-to-Peak": f"{6.60 + random.uniform(-0.1, 0.1):.4f}",
        "RMS":          f"{2.33 + random.uniform(-0.03, 0.03):.4f}",
    }


def _generator_row(resource: str, channel: int, waveform: str, freq: float) -> dict:
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "Resource":  resource,
        "Channel":   channel,
        "Time":      ts,
        "Waveform":  waveform,
        "Frequency": f"{freq:.2f}",
        "Amplitude": f"{3.30:.2f}",
        "Offset":    f"{0.00:.2f}",
        "Phase":     f"{0.00:.2f}",
    }


def inject_mock_data(window, device: str = "oscilloscope", rows: int = 5):
    """
    Inject mock rows into the MeasurementDisplay of the given MainWindow.

    Args:
        window:  MainWindow instance
        device:  "oscilloscope" or "generator"
        rows:    number of rows to add
    """
    display = window.measurement_display
    resource = "MOCK::RESOURCE::0001"
    channel = 1

    for _ in range(rows):
        if device == "generator":
            data = _generator_row(resource, channel, waveform="SINE", freq=1000.0)
        else:
            data = _oscilloscope_row(resource, channel, base_freq=1000.0)
        display.add_measurement(data)