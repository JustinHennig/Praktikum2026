from PySide6.QtWidgets import (
    QGroupBox, QHBoxLayout, QLabel, QVBoxLayout, QComboBox, QPushButton
)
from PySide6.QtGui import QPalette, QColor

from app.services.device_functions import ask_idn, scan_for_devices

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

        # Signals
        self.scan_btn.clicked.connect(self.scan_for_devices)
        self.idn_btn.clicked.connect(self.ask_idn)

    def scan_for_devices(self):
        try:
            resources = scan_for_devices()
            self.resource_combo.clear()
            self.resource_combo.addItems(resources)
            self.status_label.setStyleSheet("color: white;")
            self.status_label.setText(f"Status: {len(resources)} device(s) found")
            self.status_label.setVisible(True)
        except Exception as e:
            self.status_label.setStyleSheet("color: red;")
            self.status_label.setText(f"Scan error: {e}")

    def ask_idn(self):
        try:
            idn = ask_idn(self.resource_combo.currentText())
            self.status_label.setStyleSheet("color: white;")
            self.status_label.setText(f"IDN: {idn}")
            self.status_label.setVisible(True)
        except Exception as e:
            self.status_label.setStyleSheet("color: red;")
            self.status_label.setText(f"IDN error: {e}")