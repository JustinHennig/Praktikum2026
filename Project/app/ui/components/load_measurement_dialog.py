from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QLabel
)

# Dialog to load all measurement settings for the user to select from
class LoadMeasurementDialog(QDialog):
    def __init__(self, settings: list[dict], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Load Measurement from Database")
        self.setMinimumSize(700, 350)
        self.selected_id = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Select a measurement configuration to load:"))

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Device", "Configuration"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        for row_data in settings:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(row_data["measurement_id"])))
            self.table.setItem(row, 1, QTableWidgetItem(row_data["device"]))
            self.table.setItem(row, 2, QTableWidgetItem(str(row_data["configuration"])))

        layout.addWidget(self.table)

        btn_row = QHBoxLayout()
        self.load_btn = QPushButton("Load")
        self.cancel_btn = QPushButton("Cancel")
        btn_row.addWidget(self.load_btn)
        btn_row.addWidget(self.cancel_btn)
        layout.addLayout(btn_row)

        self.load_btn.clicked.connect(self._on_load)
        self.cancel_btn.clicked.connect(self.reject)
        self.table.doubleClicked.connect(self._on_load)

    def _on_load(self):
        selected = self.table.currentRow()
        if selected < 0:
            return
        self.selected_id = int(self.table.item(selected, 0).text())
        self.accept()