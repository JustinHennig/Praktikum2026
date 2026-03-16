import pyvisa
import csv
from instruments.SDG_Generator import SDG
from instruments.SDS_Oscilloscope import SDS

rm = pyvisa.ResourceManager()
scope = SDS(rm.open_resource('USB0::0xF4EC::0x1008::SDS5XHEC6R0118::INSTR'))
gen = SDG(rm.open_resource('USB0::0xF4EC::0x1103::SDG1XDDD805314::INSTR'))

gen.set_sine(3000, 2)
gen.output_on()

freq = scope.measure_freq()
amp = scope.measure_pkpk()

print(freq, amp)


