import pyvisa

rm = pyvisa.ResourceManager()
instrument = rm.open_resource("USB0::0xF4EC::0xEE38::SDS123456::INSTR")

print(instrument.query("*IDN?"))

instrument.write("SOUR:VOLT 5")
voltage = instrument.query("MEAS:VOLT?")
print(voltage)

instrument.close()