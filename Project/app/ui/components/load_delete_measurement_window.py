# This file defines the LoadMeasurementDialog class, which is using a QDialog to display all the measuremnt settings
# that are stored in the SQLite database, so that the user can select one to load the corresponding measurement

from PySide6.QtWidgets import (
    QDialog, QMessageBox, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QLabel
)

from app.database.alchemy.alchemy_methods import delete_measurement_by_id

class LoadMeasurementDialog(QDialog):
    def __init__(self, measurements: list[dict], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Load Measurement from Database")
        self.setMinimumSize(700, 350)
        self.selected_id: int | None = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Select a measurement to load:"))

        # Create a table to display measurements with 4 columns
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Date/Time", "Settings"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Fill the table with the measurements
        for row_data in measurements:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(row_data["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(row_data["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(row_data["date_time"]))
            self.table.setItem(row, 3, QTableWidgetItem(str(len(row_data.get("settings", [])))))

        layout.addWidget(self.table)

        # Buttons for loading or canceling
        btn_row = QHBoxLayout()
        self.load_btn = QPushButton("Load")
        self.delete_btn = QPushButton("Delete")
        self.cancel_btn = QPushButton("Cancel")
        btn_row.addWidget(self.load_btn)
        btn_row.addWidget(self.delete_btn)
        btn_row.addWidget(self.cancel_btn)
        layout.addLayout(btn_row)

        # Signals
        self.load_btn.clicked.connect(self._load)
        self.delete_btn.clicked.connect(self._delete)
        self.cancel_btn.clicked.connect(self.reject)
        self.table.doubleClicked.connect(self._load)

    # Helper function to get the selected row
    def _get_selected_row(self) -> int | None:
        selection_model = self.table.selectionModel()
        if selection_model is None:
            return None
    
        selected_rows = selection_model.selectedRows()
        if not selected_rows:
            return None
        
        return selected_rows[0].row()

    # Function to handle loading the selected measurement configuration
    def _load(self):
        row = self._get_selected_row()
        if row is None:
            QMessageBox.information(self, "Load", "No measurement selected.")
            return

        id_item = self.table.item(row, 0)
        if id_item is None:
            return

        self.selected_id = int(id_item.text())
        self.accept()

    # Function to handle deleting the selected measurement configuration and all its linked measurements from the database
    def _delete(self):
        row = self._get_selected_row()
        if row is None:
            QMessageBox.information(self, "Delete", "No measurement selected.")
            return
    
        id_item = self.table.item(row, 0)
        if id_item is None:
            return
        
        measurement_id = int(id_item.text())

        confirm = QMessageBox.question(
            self,
            "Delete",
            f"Delete measurement {measurement_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        
        try:
            delete_measurement_by_id(measurement_id)
            self.table.removeRow(row)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete from database:\n{e}")
        