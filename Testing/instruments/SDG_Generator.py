class SDG:
    def __init__(self, resource):
        self.inst = resource

    def idn(self):
        return self.inst.query("*IDN?").strip()

    def reset(self):
        self.inst.write("*RST")

    # --- Output ---
    def output_on(self, channel=1):
        self.inst.write(f"C{channel}:OUTP ON")

    def output_off(self, channel=1):
        self.inst.write(f"C{channel}:OUTP OFF")

    # --- Waveform ---
    def set_waveform(self, wvtp, freq, amp, offset=0, phase=0, channel=1):
        self.inst.write(f"C{channel}:BSWV WVTP,{wvtp},FRQ,{freq},AMP,{amp},OFST,{offset},PHSE,{phase}")

    def set_sine(self, freq, amp, offset=0, phase=0, channel=1):
        self.set_waveform("SINE", freq, amp, offset, phase, channel)

    def set_square(self, freq, amp, offset=0, duty=50, channel=1):
        self.inst.write(f"C{channel}:BSWV WVTP,SQUARE,FRQ,{freq},AMP,{amp},OFST,{offset},DUTY,{duty}")

    def set_ramp(self, freq, amp, offset=0, symmetry=50, channel=1):
        self.inst.write(f"C{channel}:BSWV WVTP,RAMP,FRQ,{freq},AMP,{amp},OFST,{offset},SYM,{symmetry}")

    def set_pulse(self, freq, amp, width, offset=0, channel=1):
        self.inst.write(f"C{channel}:BSWV WVTP,PULSE,FRQ,{freq},AMP,{amp},OFST,{offset},WIDTH,{width}")

    def set_dc(self, offset, channel=1):
        self.inst.write(f"C{channel}:BSWV WVTP,DC,OFST,{offset}")

    def set_noise(self, amp, offset=0, channel=1):
        self.inst.write(f"C{channel}:BSWV WVTP,NOISE,AMP,{amp},OFST,{offset}")

    # --- Parameter einzeln setzen ---
    def set_frequency(self, freq, channel=1):
        self.inst.write(f"C{channel}:BSWV FRQ,{freq}")

    def set_amplitude(self, amp, channel=1):
        self.inst.write(f"C{channel}:BSWV AMP,{amp}")

    def set_offset(self, offset, channel=1):
        self.inst.write(f"C{channel}:BSWV OFST,{offset}")

    def set_phase(self, phase, channel=1):
        self.inst.write(f"C{channel}:BSWV PHSE,{phase}")

    def set_duty(self, duty, channel=1):
        self.inst.write(f"C{channel}:BSWV DUTY,{duty}")

    # --- Query ---
    def get_waveform_params(self, channel=1):
        return self.inst.query(f"C{channel}:BSWV?").strip()