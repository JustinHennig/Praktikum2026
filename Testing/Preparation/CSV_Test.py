import csv

data = [
    {"Name": "Justin", "Alter": 16, "Stadt": "Frankfurt"},
    {"Name": "Max", "Alter": 20, "Stadt": "München"},
    {"Name": "Lisa", "Alter": "22", "Stadt": "Hamburg"}
]

with open("data.csv", "w", newline="", encoding="utf-8") as file:
    fieldnames = ["Name", "Alter", "Stadt"]

    writer = csv.DictWriter(file, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(data)

with open("data.csv", "a", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    writer.writerow(["Paul", 28, "Köln"])