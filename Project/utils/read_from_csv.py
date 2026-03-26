import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from tkinter import Tk, filedialog

DATA_DIR = Path(__file__).parent.parent / 'data'

# Datei-Auswahl-Dialog
root = Tk()
root.withdraw()
selected = filedialog.askopenfilename(
    title="Snapshot CSV auswählen",
    initialdir=DATA_DIR,
    filetypes=[("CSV-Dateien", "*.csv"), ("Alle Dateien", "*.*")],
)
root.destroy()

if not selected:
    print("Keine Datei ausgewählt.")
    exit()

path = Path(selected)
print(f"Lade: {path.name}")

df = pd.read_csv(path, comment='#')

# Zeitachse in µs umrechnen für bessere Lesbarkeit
time_us = df['time_s'] * 1e6

plt.figure(figsize=(14, 5))
plt.plot(time_us, df['voltage_V'], linewidth=0.6, color='steelblue')
plt.xlabel('Zeit (µs)')
plt.ylabel('Spannung (V)')
plt.title(path.stem)
plt.grid(True, alpha=0.4)
plt.tight_layout()
plt.show()
