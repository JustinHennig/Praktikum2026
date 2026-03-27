# This file contains the collect_measurement function, which gathers the current measurement values for a given resource and channel and returns a dictionary.

from app.scpi_commands.sds_commands import get_amplitude, get_frequency, get_offset, get_pkpk, get_rms, get_t_div, get_trigger_level, get_v_div

def collect_measurement(
    resource: str,
    channel: int,
    include_frequency: bool = False,
    include_amplitude: bool = False,
    include_pkpk: bool = False,
    include_rms: bool = False,
) -> dict:
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "Resource": resource,
        "Channel": channel,
        "Time": timestamp,
        "v_div_mv": get_v_div(resource, channel),
        "t_div_ms": get_t_div(resource),
        "offset_mv": get_offset(resource, channel),
        "trigger_level": get_trigger_level(resource),
        "Frequency": get_frequency(resource, channel) if include_frequency else None,
        "Amplitude": get_amplitude(resource, channel) if include_amplitude else None,
        "Peak-to-Peak": get_pkpk(resource, channel) if include_pkpk else None,
        "RMS": get_rms(resource, channel) if include_rms else None,
    }