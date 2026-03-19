import csv
import os
from PySide6.QtWidgets import QFileDialog, QMessageBox

def save_as_csv(measurement_data=None):
    # measurement_data needs to be passed as a parameter
    if measurement_data is None or len(measurement_data) == 0:
        QMessageBox.warning(None, "Save CSV", "No measurement data to save.")
        return

    # Choose file path
    file_path, _ = QFileDialog.getSaveFileName(None, "Save Measurements as CSV", os.getcwd(), "CSV Files (*.csv)")
    if not file_path:
        return

    # write data to CSV
    try:
        with open(file_path, mode="w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=measurement_data[0].keys())
            writer.writeheader()
            writer.writerows(measurement_data)
        QMessageBox.information(None, "Save CSV", f"Measurements saved to {file_path}")
    except Exception as e:
        QMessageBox.critical(None, "Save CSV", f"Error saving CSV: {e}")