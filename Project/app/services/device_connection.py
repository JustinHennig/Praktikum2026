import pyvisa


def scan_for_devices() -> list[str]:
    rm = pyvisa.ResourceManager()
    return list(rm.list_resources())

def ask_idn(resource: str) -> str:
    rm = pyvisa.ResourceManager()
    try:
        instrument = rm.open_resource(resource)
        idn = instrument.query("*IDN?") 
        return idn.strip()
    except Exception as e:
        raise RuntimeError(f"IDN query failed: {e}")


