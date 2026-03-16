import time
import pyvisa
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from Instruments.SDG_Generator import SDG
from Instruments.SDS_Oscilloscope import SDS

# ── VISA-Verbindung ──
rm = pyvisa.ResourceManager()

SDG_ADDR = "USB0::0xF4EC::0x1103::SDG1XDDD805314::INSTR"
SDS_ADDR = "USB0::0xF4EC::0x1008::SDS5XHEC6R0118::INSTR"

gen: SDG | None = None
scope: SDS | None = None

try:
    gen = SDG(rm.open_resource(SDG_ADDR))
    print(f"Generator verbunden: {gen.idn()}")
except Exception as e:
    print(f"Generator nicht verbunden: {e}")

try:
    scope = SDS(rm.open_resource(SDS_ADDR))
    print(f"Oszilloskop verbunden: {scope.idn()}")
except Exception as e:
    print(f"Oszilloskop nicht verbunden: {e}")

# ── FastAPI ──
app = FastAPI(title="Laborgeräte-API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Models ──
class MeasureRequest(BaseModel):
    frequency: float
    amplitude: float


# ── Endpoints ──
@app.get("/devices")
def get_devices():
    devices = []

    if gen:
        try:
            idn = gen.idn()
            devices.append({"name": "SDG6052X", "type": "generator", "connected": True, "idn": idn})
        except Exception:
            devices.append({"name": "SDG6052X", "type": "generator", "connected": False, "idn": ""})
    else:
        devices.append({"name": "SDG6052X", "type": "generator", "connected": False, "idn": ""})

    if scope:
        try:
            idn = scope.idn()
            devices.append({"name": "SDS5034X", "type": "oscilloscope", "connected": True, "idn": idn})
        except Exception:
            devices.append({"name": "SDS5034X", "type": "oscilloscope", "connected": False, "idn": ""})
    else:
        devices.append({"name": "SDS5034X", "type": "oscilloscope", "connected": False, "idn": ""})

    return devices


@app.post("/measure")
def measure(req: MeasureRequest):
    if not gen or not scope:
        raise HTTPException(status_code=503, detail="Geräte nicht verbunden")

    # Generator: Sinus mit gewünschter Frequenz + Amplitude einstellen
    gen.set_sine(req.frequency, req.amplitude)
    gen.output_on(channel=1)

    # Oszilloskop: Messung vorbereiten
    scope.auto_setup()
    time.sleep(2)

    scope.measure_setup(source=1)
    scope.measure_item_on("FREQ")
    scope.measure_item_on("AMPL")
    time.sleep(1)

    # Messwerte auslesen
    freq = scope.measure_freq()
    ampl = scope.measure_ampl()

    return {"frequency": freq, "amplitude": ampl}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)