# This file contains the SweepMeasurement class, which is responsible for performing sweep measurements with the SDS oscilloscope.

import time
import numpy as np
from app.scpi_commands.sdg_commands import set_frequency
from app.scpi_commands.sds_commands import get_amplitude, get_pkpk, get_rms

def run_sweep(
    sdg_resource: str,
    sds_resource: str,
    sdg_channel: int,
    sds_channel: int,
    start_freq: float,
    stop_freq: float,
    step: int,
    settle_time_ms: int = 200,
) -> list[dict]:
    frequencies = np.arange(start_freq, stop_freq + step, step)
    results = []
    for freq in frequencies:
        set_frequency(sdg_resource, freq, sdg_channel)
        time.sleep(settle_time_ms / 1000)
        results.append({
            "Frequency_Hz": round(freq, 4),
            "Amplitude":    get_amplitude(sds_resource, sds_channel),
            "Peak-to-Peak": get_pkpk(sds_resource, sds_channel),
            "RMS":          get_rms(sds_resource, sds_channel),
        })
    return results