# This file contains functions for controlling the generator using SCPI Commands via PyVISA

from app.scpi_commands.device_independent_commands import open_message_resource

# Generator functions
def set_waveform(resource: str, waveform:str, channel: int):
    inst = open_message_resource(resource)
    inst.write(f'C{channel}:BSWV WVTP,{waveform}')

def set_frequency(resource: str, frequency: float, channel: int):
    inst = open_message_resource(resource)
    inst.write(f'C{channel}:BSWV FRQ,{frequency:.6f}')

def set_amplitude(resource: str, amplitude: float, channel: int):
    inst = open_message_resource(resource)
    inst.write(f'C{channel}:BSWV AMP,{amplitude:.6f}')

def set_offset_gen(resource: str, offset: float, channel: int):
    inst = open_message_resource(resource)
    inst.write(f'C{channel}:BSWV OFST,{offset:.3f}')

def set_phase(resource: str, phase: float, channel: int):
    inst = open_message_resource(resource)
    inst.write(f'C{channel}:BSWV PHSE,{phase:.3f}')

def set_output(resource: str, channel: int) -> str:
    inst = open_message_resource(resource)
    status = inst.query(f'C{channel}:OUTP?').strip()
    if 'OFF' in status:
        inst.write(f'C{channel}:OUTP ON')
        return 'ON'
    else:
        inst.write(f'C{channel}:OUTP OFF')
        return 'OFF'
    
# Function to get the current output status of a generator channel
def get_output_status(resource: str, channel: int) -> str:
    inst = open_message_resource(resource)
    status = inst.query(f'C{channel}:OUTP?').strip()
    if 'OFF' in status:
        return 'OFF'
    else:
        return 'ON'