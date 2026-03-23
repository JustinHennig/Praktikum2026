# This file defines the ConnectionPanel class, which is using QGroupBox to display the connection options for the devices

from PySide6.QtWidgets import (
    QGroupBox, QHBoxLayout, QLabel, QVBoxLayout, QComboBox, QPushButton
)
from PySide6.QtCore import QThread
from app.scpi_commands.device_independent_commands import scan_for_devices, ask_idn
from app.services.device_worker import DeviceWorker

class ConnectionPanel(QGroupBox):
    def __init__(self):
        super().__init__("Connection Panel")

        layout = QVBoxLayout(self)

        # Selecting the device type
        device_type_row = QHBoxLayout()
        device_type_row.addWidget(QLabel("Device Type:"))
        self.device_combo = QComboBox()
        self.device_combo.setEditable(False)
        self.device_combo.addItems(["Oscilloscope", "Function Generator"])
        device_type_row.addWidget(self.device_combo)
        layout.addLayout(device_type_row)

        # Select the resource
        resource_row = QHBoxLayout()
        resource_row.addWidget(QLabel("Resource:"))
        self.resource_combo = QComboBox()
        self.resource_combo.setEditable(False)
        self.resource_combo.view().setMinimumWidth(400)
        resource_row.addWidget(self.resource_combo)
        layout.addLayout(resource_row)

        # Buton Row
        btn_row = QHBoxLayout()
        self.scan_btn = QPushButton("Scan for devices")
        self.idn_btn = QPushButton("Ask IDN")
        btn_row.addWidget(self.scan_btn)
        btn_row.addWidget(self.idn_btn)
        layout.addLayout(btn_row)

        # Status
        self.status_label = QLabel("Status: Disconnected")
        self.status_label.setStyleSheet("color: white;")
        self.status_label.setVisible(False)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        # Worker thread for device-independent SCPI operations (scan, IDN)
        self._worker = DeviceWorker()
        self._thread = QThread(self)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.result_ready.connect(self._on_result)
        self._worker.error_occurred.connect(self._on_error)
        self._thread.start()

        # Signals
        self.scan_btn.clicked.connect(self.scan_for_devices)
        self.idn_btn.clicked.connect(self.ask_idn)

    # Function to scan for devices and update the resource combo box using the scan_for_devices function from device_functions.py
    def scan_for_devices(self):
        self.scan_btn.setEnabled(False)
        self.status_label.setStyleSheet("color: white;")
        self.status_label.setText("Scanning...")
        self.status_label.setVisible(True)
        self._worker.submit("scan", scan_for_devices)

    # Function to ask the IDN of the selected device using the ask_idn function from device_functions.py
    def ask_idn(self):
        resource = self.resource_combo.currentText()
        if not resource:
            return
        self.idn_btn.setEnabled(False)
        self.status_label.setStyleSheet("color: white;")
        self.status_label.setText("Asking IDN...")
        self.status_label.setVisible(True)
        self._worker.submit("idn", ask_idn, resource)

    def _on_result(self, task_id: str, result):
        match task_id:
            case "scan":
                self.scan_btn.setEnabled(True)
                self.resource_combo.clear()
                self.resource_combo.addItems(result)
                self.status_label.setStyleSheet("color: white;")
                self.status_label.setText(f"Status: {len(result)} device(s) found")
            case "idn":
                self.idn_btn.setEnabled(True)
                self.status_label.setStyleSheet("color: white;")
                self.status_label.setText(f"IDN: {result}")

    def _on_error(self, task_id: str, error: str):
        match task_id:
            case "scan":
                self.scan_btn.setEnabled(True)
                self.status_label.setStyleSheet("color: red;")
                self.status_label.setText(f"Scan error: {error}")
            case "idn":
                self.idn_btn.setEnabled(True)
                self.status_label.setStyleSheet("color: red;")
                self.status_label.setText(f"IDN error: {error}")