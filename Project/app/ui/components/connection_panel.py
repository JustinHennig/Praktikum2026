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

        # Two comboboxes for two resources, one for the oscilloscope and one for the function generator for ease of use
        resource_layout = QVBoxLayout()
        osc_resource_row = QHBoxLayout()
        osc_resource_row.addWidget(QLabel("Oscilloscope Resource:"))
        self.osc_resource_combo = QComboBox()
        self.osc_resource_combo.setEditable(False)
        self.osc_resource_combo.view().setMinimumWidth(400)
        osc_resource_row.addWidget(self.osc_resource_combo)

        gen_resource_row = QHBoxLayout()
        gen_resource_row.addWidget(QLabel("Function Generator Resource:"))
        self.gen_resource_combo = QComboBox()
        self.gen_resource_combo.setEditable(False)
        self.gen_resource_combo.view().setMinimumWidth(400)
        gen_resource_row.addWidget(self.gen_resource_combo)

        resource_layout.addLayout(osc_resource_row)
        resource_layout.addLayout(gen_resource_row)
        layout.addLayout(resource_layout)

        # Button Row
        btn_row = QHBoxLayout()
        self.scan_btn = QPushButton("Scan for devices")
        self.idn_btn = QPushButton("Ask IDN")
        btn_row.addWidget(self.scan_btn)
        btn_row.addWidget(self.idn_btn)
        layout.addLayout(btn_row)

        # Status
        self.status_label = QLabel("Status: Disconnected")
        self.status_label.setStyleSheet("")
        self.status_label.setContentsMargins(0, 10, 0, 0)
        self.status_label.setWordWrap(True)
        self.status_label.setVisible(False)
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
        self.status_label.setStyleSheet("")
        self.status_label.setText("Scanning...")
        self.status_label.setVisible(True)
        self._worker.submit("scan", scan_for_devices)

    # Function to ask the IDN of the selected device using the ask_idn function from device_functions.py
    def ask_idn(self):
        device_type = self.device_combo.currentText()
        if device_type == "Oscilloscope":
            resource = self.osc_resource_combo.currentText()
        elif device_type == "Function Generator":
            resource = self.gen_resource_combo.currentText()
        else:
            return
        if not resource:
            return
        self.idn_btn.setEnabled(False)
        self.status_label.setStyleSheet("")
        self.status_label.setText("Asking IDN...")
        self.status_label.setVisible(True)
        self._worker.submit("idn", ask_idn, resource)

    # Callback functions for the worker thread to update the UI based on the results or errors from the scan and IDN operations
    def _on_result(self, task_id: str, result):
        match task_id:
            case "scan":
                self.scan_btn.setEnabled(True)
                self.osc_resource_combo.clear()
                self.osc_resource_combo.addItems(result)
                self.gen_resource_combo.clear()
                self.gen_resource_combo.addItems(result)
                self.status_label.setStyleSheet("")
                self.status_label.setText(f"Status: {len(result)} device(s) found")
            case "idn":
                self.idn_btn.setEnabled(True)
                self.status_label.setStyleSheet("")
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

    # Clean up the worker thread when the panel is closed
    def cleanup(self):
        self._worker.stop()
        self._thread.quit()
        self._thread.wait()