import pyvisa
rm = pyvisa.ResourceManager()

def scan_for_devices() -> list[str]:
    return list(rm.list_resources())

def ask_idn(resource: str) -> str:
    try:
        instrument = rm.open_resource(resource)
        idn = instrument.query("*IDN?") 
        return idn.strip()
    except Exception as e:
        raise RuntimeError(f"IDN query failed: {e}")

# Oscilloscope funcions
def auto_set(resource: str):
    inst = rm.open_resource(resource)
    inst.write(':AUTOset')

# get values
def get_v_div(resource: str, channel: int) -> str:
    inst = rm.open_resource(resource)
    v_div = float(inst.query(f':CHAN{channel}:SCAL?').strip()) * 1000
    return f"{v_div:.2f}"

def get_t_div(resource: str) -> str:
    inst = rm.open_resource(resource)
    t_div = float(inst.query(':TIM:SCAL?').strip()) * 1000
    return f"{t_div:.2f}"

def get_offset(resource: str, channel: int) -> str:
    inst = rm.open_resource(resource)
    offset = float(inst.query(f':CHAN{channel}:OFFS?').strip()) * 1000
    return f"{offset:.2f}"

def get_trigger_level(resource: str) -> str:
    inst = rm.open_resource(resource)
    trigger_level = float(inst.query(':TRIG:EDGE:LEV?').strip()) * 1000
    return f"{trigger_level:.2f}"

# set values
def set_v_div(resource: str, v_div: float, channel: int):
    inst = rm.open_resource(resource)
    inst.write(f':CHAN{channel}:SCAL {v_div / 1000:.6f}')

def set_t_div(resource: str, t_div: float):
    inst = rm.open_resource(resource)
    inst.write(f':TIM:SCAL {t_div / 1000:.6f}')

def set_offset(resource: str, offset: float, channel: int):
    inst = rm.open_resource(resource)
    inst.write(f':CHAN{channel}:OFFS {offset / 1000:.6f}')

def set_trigger_level(resource: str, trigger_level: float):
    inst = rm.open_resource(resource)
    inst.write(f':TRIG:EDGE:LEV {trigger_level / 1000:.6f}')

# Generator functions
def set_waveform(resource: str, waveform:str, channel: int):
    inst = rm.open_resource(resource)
    inst.write(f'C{channel}:BSWV WVTP,{waveform}')

def set_frequency(resource: str, frequency: float, channel: int):
    inst = rm.open_resource(resource)
    inst.write(f'C{channel}:BSWV FRQ,{frequency:.6f}')

def set_amplitude(resource: str, amplitude: float, channel: int):
    inst = rm.open_resource(resource)
    inst.write(f'C{channel}:BSWV AMP,{amplitude:.6f}')

def set_offset_gen(resource: str, offset: float, channel: int):
    inst = rm.open_resource(resource)
    inst.write(f'C{channel}:BSWV OFST,{offset:.3f}')

def set_phase(resource: str, phase: float, channel: int):
    inst = rm.open_resource(resource)
    inst.write(f'C{channel}:BSWV PHSE,{phase:.3f}')

def set_output(resource: str, channel: int) -> str:
    inst = rm.open_resource(resource)
    status = inst.query(f'C{channel}:OUTP?').strip()
    if 'OFF' in status:
        inst.write(f'C{channel}:OUTP ON')
        return 'ON'
    else:
        inst.write(f'C{channel}:OUTP OFF')
        return 'OFF'
    
def get_output_status(resource: str, channel: int) -> str:
    inst = rm.open_resource(resource)
    status = inst.query(f'C{channel}:OUTP?').strip()
    if 'OFF' in status:
        return 'OFF'
    else:
        return 'ON'