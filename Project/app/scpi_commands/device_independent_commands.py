# This file contains SCPI command functions that are usually same for different devices.

import pyvisa
from typing import cast
from pyvisa.resources import MessageBasedResource

# Function to open a message-based resource and cast it to the correct type for better type checking
def open_message_resource(resource: str) -> MessageBasedResource:
    return cast(MessageBasedResource, pyvisa.ResourceManager().open_resource(resource))

def scan_for_devices() -> list[str]:
    return list(pyvisa.ResourceManager().list_resources())

def ask_idn(resource: str) -> str:
    try:
        inst = open_message_resource(resource)
        idn = inst.query("*IDN?") 
        return idn.strip()
    except Exception as e:
        raise RuntimeError(f"IDN query failed: {e}")
