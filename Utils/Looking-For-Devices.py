import pyvisa

rm = pyvisa.ResourceManager()
resources = rm.list_resources()

if not resources:
    print("Keine Geräte gefunden.")
else:
    print(f"{len(resources)} Gerät(e) gefunden:\n")
    for addr in resources:
        print(f"  {addr}")