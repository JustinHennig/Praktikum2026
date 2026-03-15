import csv

data = [
    ["Name", "Alter", "Stadt"],
    ["Justin", "16", "Frankfurt"],
    ["Max", "20", "München"],
    ["Lisa", "22", "Hamburg"]
]

with open("data.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    for row in data:
        writer.writerow(row)