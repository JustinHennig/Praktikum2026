import pyvisa
rm = pyvisa.ResourceManager()

def get_frequency(resource: str):
    inst = rm.open_resource(resource)
    freq = float(inst.query(':TRIG:FREQ?').strip())
    return f"{freq:.4f}"

def get_amplitude(resoruce: str, channel: int):
    inst = rm.open_resource(resoruce)
    inst.write(f':MEAS:SIMP:SOUR C{channel}')
    ampl = float(inst.query(':MEAS:SIMP:VAL? AMPL').strip())
    return f"{ampl:.4f}"

def get_pkpk(resource: str, channel: int):
    inst = rm.open_resource(resource)
    inst.write(f':MEAS:SIMP:SOUR C{channel}')
    pkpk = float(inst.query(':MEAS:SIMP:VAL? PKPK').strip())
    return f"{pkpk:.4f}"

def get_rms(resource: str, channel: int):
    inst = rm.open_resource(resource)
    inst.write(f':MEAS:SIMP:SOUR C{channel}')
    rms = float(inst.query(':MEAS:SIMP:VAL? RMS').strip())
    return f"{rms:.4f}"