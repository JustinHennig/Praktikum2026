# This file contains functions for getting additional measurements from the oscilloscope.

from typing import cast
from pyvisa.resources import MessageBasedResource

def open_message_resource(resource: str) -> MessageBasedResource:
    return cast(MessageBasedResource, open_message_resource(resource))

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