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
def get_frequency(resource: str):
    inst = open_message_resource(resource)
    freq = float(inst.query(':TRIG:FREQ?').strip())
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