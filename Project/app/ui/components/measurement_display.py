# This file defines the MeasurementDisplay class, which is using a QGroupbox to display
# the measurement data in a table and also provides buttons to save the data, load the data, clear the display and delete a selected row.

from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QHeaderView, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QDialog
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from app.database.alchemy.alchemy_methods import insert_measurement, insert_measurement_setting, insert_measurement_value, get_values_by_setting_id, get_all_measurements
from app.ui.components.load_delete_measurement_window import LoadMeasurementDialog

_UNITS = {
    "Elapsed_Time": "Time (s)",
    "Frequency":    "Frequency (Hz)",
    "Amplitude":    "Amplitude (V)",
    "Peak-to-Peak": "Peak-to-Peak (V)",
    "RMS":          "RMS (V)",
    "Waveform":     "Waveform",
    "Offset":       "Offset (V)",
    "Phase":        "Phase (°)",
}

class MeasurementDisplay(QGroupBox):
    # Signal to notify the main window that a new measurement has been added, so that the configuration can be updated
    configuration_loaded = Signal(dict)

    def __init__(self):
        super().__init__("Measurement Display")

        layout = QVBoxLayout(self)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Time", "Col. 1", "Col. 2", "Col. 3", "Col. 4"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        # Buttons for saving
        button_row = QHBoxLayout()

        self.save_db_btn = QPushButton("Save to Database")
        self.load_db_btn = QPushButton("Load from Database")
        self.clear_btn = QPushButton("Clear Display")
        self.delete_row_btn = QPushButton("Delete Row")

        button_row.addWidget(self.save_db_btn)
        button_row.addWidget(self.load_db_btn)
        button_row.addWidget(self.clear_btn)
        button_row.addWidget(self.delete_row_btn)
        layout.addLayout(button_row)

        # Signals
        self.save_db_btn.clicked.connect(self._insert_measurement_into_db)
        self.load_db_btn.clicked.connect(self._load_measurements_from_db)
        self.clear_btn.clicked.connect(self.clear_display)
        self.delete_row_btn.clicked.connect(self._delete_selected_row)

        # Initialize measurement data list
        self.measurement_data = []
        self.measurement_name = ""
        self._columns: list = []  # stores the column keys once the first real row arrives

    def set_measurement_name(self, name: str):
        self.measurement_name = name.strip()

    # Function to add measurement data to the display
    def add_measurement(self, data):
        self.measurement_data.append(data)

        # Keys to display — skip metadata that is not useful in the table
        skip_keys = {"Resource", "Channel", "Time", "v_div_mv", "t_div_ms", "offset_mv", "trigger_level"}
        other_cols = [k for k in data if k not in skip_keys and k != "Elapsed_Time"]
        columns = (["Elapsed_Time"] if "Elapsed_Time" in data else []) + other_cols

        # Set headers on the very first real data row
        if not self._columns:
            self._columns = columns
            self.table.setColumnCount(len(columns))
            self.table.setHorizontalHeaderLabels([_UNITS.get(c, c) for c in columns])
            # Re-span any separator rows that were inserted before columns were known
            for r in range(self.table.rowCount()):
                if self.table.columnSpan(r, 0) > 1:
                    self.table.setSpan(r, 0, 1, len(columns))

        row = self.table.rowCount()
        self.table.insertRow(row)
        for col, key in enumerate(self._columns):
            value = data.get(key)
            self.table.setItem(row, col, QTableWidgetItem("" if value is None else str(value)))

    # Insert a full-width separator row to visually group measurement settings
    def add_separator(self, label: str):
        col_count = len(self._columns) if self._columns else self.table.columnCount()
        self.measurement_data.append({"__separator__": label})
        row = self.table.rowCount()
        self.table.insertRow(row)
        item = QTableWidgetItem(label)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setBold(True)
        item.setFont(font)
        self.table.setItem(row, 0, item)
        self.table.setSpan(row, 0, 1, max(col_count, 1))

    def _insert_measurement_into_db(self):
        real_data = [d for d in self.measurement_data if "__separator__" not in d]
        if not real_data:
            return

        # Keys that are never stored as measurement values
        meta_keys = {"Resource", "Time", "Elapsed_Time", "Name"}
        # Keys that describe the instrument configuration → go into 'parameters'
        config_keys = {"Channel", "v_div_mv", "t_div_ms", "offset_mv", "trigger_level"}

        first = real_data[0]

        # Device is identified by the instrument resource address
        device = first.get("Resource", "Unknown")

        # Configuration: channel + oscilloscope settings (ignored for generator since those keys won't exist)
        parameters = {k: v for k, v in first.items() if k in config_keys}

        # Measurement value keys: everything that is not metadata or configuration
        measurement_keys = [k for k in first if k not in meta_keys and k not in config_keys]

        try:
            measurement_id = insert_measurement(
                name=self.measurement_name or "Unnamed Measurement",
                date_time=first.get("Time", ""),
            )
            setting_id = insert_measurement_setting(
                measurement_id=measurement_id,
                device=device,
                configuration=parameters,
            )
            for data in real_data:
                values = {k: data.get(k) for k in measurement_keys}
                insert_measurement_value(
                    measurement_setting_id=setting_id,
                    time=data.get("Elapsed_Time", ""),
                    values=values
                )
            QMessageBox.information(
                self,
                "Saved",
                f"{len(real_data)} measurement(s) saved to the database."
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save to database:\n{e}")

    # Function to load the measurement data from the database and display it in the table
    def _load_measurements_from_db(self):
        measurements = get_all_measurements()
        if not measurements:
            QMessageBox.information(self, "Load", "No measurements found in the database.")
            return

        dialog = LoadMeasurementDialog(measurements, parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        if dialog.selected_id is None:
            QMessageBox.information(self, "Load", "No measurement selected.")
            return

        # Find the selected measurement and load all settings with separator rows
        selected = next((m for m in measurements if m["id"] == dialog.selected_id), None)
        if selected is None or not selected["settings"]:
            QMessageBox.information(self, "Load", "No data rows for this measurement.")
            return

        # Emit configuration for the first setting so the device panel can restore its state
        first_setting = selected["settings"][0]
        self.configuration_loaded.emit({
            "name": selected["name"],
            "configuration": first_setting["configuration"],
        })

        self.clear_display()
        for setting in selected["settings"]:
            self.add_separator(f"Measurement Setting {setting['id']}")
            values = get_values_by_setting_id(setting["id"])
            for v in values:
                data = {"Elapsed_Time": v["time"], **v["values"]}
                self.add_measurement(data)

    # Function to clear the display
    def clear_display(self):
        self.table.setRowCount(0)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Time", "Col. 1", "Col. 2", "Col. 3", "Col. 4"])
        self.measurement_data.clear()
        self._columns = []

    # Function to delete the selected row
    def _delete_selected_row(self):
        if not self.table.selectionModel().hasSelection():
            QMessageBox.information(self, "Delete Row", "No row selected.")
            return
        selected_row = self.table.currentRow()
        self.table.removeRow(selected_row)
        # Only delete if index exists in measurement_data
        if 0 <= selected_row < len(self.measurement_data):
            del self.measurement_data[selected_row]