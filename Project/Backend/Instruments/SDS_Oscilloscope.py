class SDS:
    def __init__(self, resource):
        self.inst = resource

    def idn(self):
        return self.inst.query("*IDN?").strip()

    def reset(self):
        self.inst.write("*RST")

    def auto_setup(self):
        self.inst.write("ASET")

    # --- Zeitbasis ---
    def set_tdiv(self, tdiv):
        self.inst.write(f"TDIV {tdiv}")

    def get_tdiv(self):
        return self.inst.query("TDIV?").strip()

    # --- Vertikal ---
    def set_vdiv(self, vdiv, channel=1):
        self.inst.write(f"C{channel}:VDIV {vdiv}")

    def set_offset(self, offset, channel=1):
        self.inst.write(f"C{channel}:OFST {offset}")

    def set_coupling(self, coupling, channel=1):
        """coupling: A1M (AC 1MOhm), D1M (DC 1MOhm), D50 (DC 50Ohm), GND"""
        self.inst.write(f"C{channel}:CPL {coupling}")

    def channel_on(self, channel=1):
        self.inst.write(f"C{channel}:TRA ON")

    def channel_off(self, channel=1):
        self.inst.write(f"C{channel}:TRA OFF")

    # --- Trigger ---
    def set_trigger_level(self, level, channel=1):
        self.inst.write(f"C{channel}:TRLV {level}")

    def set_trigger_mode(self, mode):
        """mode: AUTO, NORM, SINGLE, STOP"""
        self.inst.write(f"TRMD {mode}")

    def force_trigger(self):
        self.inst.write("FRTR")

    # --- Acquisition ---
    def run(self):
        self.inst.write("TRMD AUTO")

    def stop(self):
        self.inst.write("STOP")

    def single(self):
        self.inst.write("TRMD SINGLE")

    # --- Messung ---
    def measure_setup(self, source=1):
        self.inst.write("MEAS ON")
        self.inst.write("MEAS:MODE SIMP")
        self.inst.write(f"MEAS:SIMP:SOUR C{source}")

    def measure_item_on(self, item, source=1):
        """item: FREQ, PKPK, AMPL, RMS, RISE, FALL, PER, DUTY, MAX, MIN, ..."""
        self.inst.write(f"MEAS:SIMP:SOUR C{source}")
        self.inst.write(f"MEAS:SIMP:ITEM {item},ON")

    def measure(self, item):
        return self.inst.query(f"MEAS:SIMP:VAL? {item}").strip()

    def measure_freq(self):
        return self.measure("FREQ")

    def measure_pkpk(self):
        return self.measure("PKPK")

    def measure_ampl(self):
        return self.measure("AMPL")

    def measure_rms(self):
        return self.measure("RMS")

    def measure_rise(self):
        return self.measure("RISE")

    def measure_fall(self):
        return self.measure("FALL")

    def measure_period(self):
        return self.measure("PER")

    def measure_duty(self):
        return self.measure("DUTY")

    def measure_max(self):
        return self.measure("MAX")

    def measure_min(self):
        return self.measure("MIN")