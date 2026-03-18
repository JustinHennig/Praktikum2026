from PySide6.QtWidgets import (
    QGroupBox, QHBoxLayout, QLabel, QVBoxLayout, QComboBox
)
from PySide6.QtGui import QPalette, QColor

class OscilloscopeConfigurePanel(QGroupBox):
    def __init__(self):
        super().__init__("Oscilloscope Configure Panel")

        layout = QVBoxLayout(self)

        # Channel configuration
        channel_row = QHBoxLayout()
        channel_row.addWidget(QLabel("Channel:"))
        self.channel_combo = QComboBox()
        self.channel_combo.setEditable(False)
        self.channel_combo.addItems(["1", "2", "3", "4"])
        channel_row.addWidget(self.channel_combo)
        layout.addLayout(channel_row)

class FunctionGeneratorConfigurePanel(QGroupBox):
    # Placeholder for future function generator configuration panel
    def __init__(self):
        super().__init__("Function Generator Configure Panel")

        layout = QVBoxLayout(self)

        # Channel configuration
        channel_row = QHBoxLayout()
        channel_row.addWidget(QLabel("Channel:"))
        self.channel_combo = QComboBox()
        self.channel_combo.setEditable(False)
        self.channel_combo.addItems(["1", "2"])
        channel_row.addWidget(self.channel_combo)
        layout.addLayout(channel_row)