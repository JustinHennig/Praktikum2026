import pyvisa
import time
import csv
import sqlite3
from instruments.SDG_Generator import SDG
from instruments.SDS_Oscilloscope import SDS

rm = pyvisa.ResourceManager()
scope = SDS(rm.open_resource('USB0::0xF4EC::0x1008::SDS5XHEC6R0118::INSTR'))
gen = SDG(rm.open_resource('USB0::0xF4EC::0x1103::SDG1XDDD805314::INSTR'))

print(scope.idn())
print(gen.idn())

gen.set_sine(3000, 2)

scope.measure_setup(source=1)
scope.measure_item_on("FREQ")
scope.measure_item_on("AMPL")

# Verschieden Frequenzen einstellen und messen
frequencies = [500, 1000, 2000, 3000]
results = []

for f in frequencies:
    gen.set_frequency(f)
    time.sleep(1)
    freq = scope.measure_freq()
    ampl = scope.measure_pkpk()
    results.append([f, freq, ampl])

#Ergebnise in einer SQLite-Datenbank speichern
db = sqlite3.connect("sweep_results.db")
cursor = db.cursor()

cursor.execute("""
         CREATE TABLE IF NOT EXISTS sweep (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               freq_set REAL,
               freq_measured TEXT,
               amplitude TEXT
               )      
               """)

for f in frequencies:
    gen.set_frequency(f)
    time.sleep(1)
    freq = scope.measure_freq()
    ampl = scope.measure_pkpk()
    cursor.execute("INSERT INTO sweep (freq_set, freq_measured, amplitude) VALUES (?, ?, ?)", (f, freq, ampl))

db.commit()
db.close()