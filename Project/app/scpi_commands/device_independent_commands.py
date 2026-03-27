# This file contains SCPI command functions that are usually same for different devices.

import pyvisa
from typing import cast
from pyvisa.resources import MessageBasedResource

_rm = pyvisa.ResourceManager()
_resource_cache: dict[str, MessageBasedResource] = {}

# Returns a cached open connection for the given resource, opening it once on first access.
def open_message_resource(resource: str) -> MessageBasedResource:
    if resource not in _resource_cache:
        _resource_cache[resource] = cast(MessageBasedResource, _rm.open_resource(resource))
    return _resource_cache[resource]

def scan_for_devices() -> list[str]:
    return list(_rm.list_resources())

def ask_idn(resource: str) -> str:
    try:
        inst = open_message_resource(resource)
        idn = inst.query("*IDN?") 
        return idn.strip()
    except Exception as e:
        raise RuntimeError(f"IDN query failed: {e}")
