# This file contains functions for controlling the oscilloscope and generator, as well as scanning for devices and asking for their IDN.

from app.scpi_commands.device_independent_commands import open_message_resource

# Oscilloscope funcions
def auto_set(resource: str):
    inst = open_message_resource(resource)
    inst.write(':AUTOset')

# get values
def get_v_div(resource: str, channel: int) -> str:
    inst = open_message_resource(resource)
    v_div = float(inst.query(f':CHAN{channel}:SCAL?').strip()) * 1000
    return f"{v_div:.4f}"

def get_t_div(resource: str) -> str:
    inst = open_message_resource(resource)
    t_div = float(inst.query(':TIM:SCAL?').strip()) * 1000
    return f"{t_div:.4f}"

def get_offset(resource: str, channel: int) -> str:
    inst = open_message_resource(resource)
    offset = float(inst.query(f':CHAN{channel}:OFFS?').strip()) * 1000
    return f"{offset:.4f}"

def get_trigger_level(resource: str) -> str:
    inst = open_message_resource(resource)
    trigger_level = float(inst.query(':TRIG:EDGE:LEV?').strip()) * 1000
    return f"{trigger_level:.4f}"

# set values
def set_v_div(resource: str, v_div: float, channel: int):
    inst = open_message_resource(resource)
    inst.write(f':CHAN{channel}:SCAL {v_div / 1000:.6f}')

def set_t_div(resource: str, t_div: float):
    inst = open_message_resource(resource)
    inst.write(f':TIM:SCAL {t_div / 1000:.6f}')

def set_offset(resource: str, offset: float, channel: int):
    inst = open_message_resource(resource)
    inst.write(f':CHAN{channel}:OFFS {offset / 1000:.6f}')

def set_trigger_level(resource: str, trigger_level: float):
    inst = open_message_resource(resource)
    inst.write(f':TRIG:EDGE:LEV {trigger_level / 1000:.6f}')

# Functions to get measurement values from the oscilloscope
def get_frequency(resource: str, channel: int):
    inst = open_message_resource(resource)
    inst.write(f':MEAS:SIMP:SOUR C{channel}')
    freq = float(inst.query(':MEAS:SIMP:VAL? FREQ').strip())
    return f"{freq:.4f}"

def get_amplitude(resource: str, channel: int):
    inst = open_message_resource(resource)
    inst.write(f':MEAS:SIMP:SOUR C{channel}')
    ampl = float(inst.query(':MEAS:SIMP:VAL? AMPL').strip())
    return f"{ampl:.4f}"

def get_pkpk(resource: str, channel: int):
    inst = open_message_resource(resource)
    inst.write(f':MEAS:SIMP:SOUR C{channel}')
    pkpk = float(inst.query(':MEAS:SIMP:VAL? PKPK').strip())
    return f"{pkpk:.4f}"

def get_rms(resource: str, channel: int):
    inst = open_message_resource(resource)
    inst.write(f':MEAS:SIMP:SOUR C{channel}')
    rms = float(inst.query(':MEAS:SIMP:VAL? RMS').strip())
    return f"{rms:.4f}"

# Methods for the snapshot functionality
def start_trigger(resource: str):
    inst = open_message_resource(resource)
    inst.write(':TRIGger:RUN')

def stop_trigger(resource: str):
    inst = open_message_resource(resource)
    inst.write(':TRIGger:STOP')

def set_waveform_source(resource: str, channel: int):
    inst = open_message_resource(resource)
    inst.write(f':WAVeform:SOURce C{channel}')

def set_waveform_start(resource: str, start: int):
    inst = open_message_resource(resource)
    inst.write(f':WAVeform:STARt {start}')

def set_waveform_width(resource: str, width: str):
    inst = open_message_resource(resource)
    inst.write(f':WAVeform:WIDTh {width}')

def get_preamble(resource: str) -> bytes:
    inst = open_message_resource(resource)
    inst.write(':WAVeform:PREamble?')
    return inst.read_raw()

def get_max_points(resource: str) -> int:
    inst = open_message_resource(resource)
    max_points = int(inst.query(':WAVeform:MAXPoint?').strip())
    return max_points

def set_waveform_points(resource: str, points: int):
    inst = open_message_resource(resource)
    inst.write(f':WAVeform:POINt {points}')

def get_waveform_data(resource: str) -> bytes:
    inst = open_message_resource(resource)
    inst.write(':WAVeform:DATA?')
    return inst.read_raw()
