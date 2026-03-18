from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt

from app.ui.components.measurement_display import MeasurementDisplay
from app.ui.components.device_configure_panels import OscilloscopeConfigurePanel
from app.ui.components.connection_panel import ConnectionPanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Measurement App for SCPI Instruments")
        self.setMinimumSize(1100, 600)

        layoutWhole = QHBoxLayout()
        layoutLeftSide = QVBoxLayout()

        layoutWhole.addLayout(layoutLeftSide, stretch=2)
        layoutWhole.addWidget(MeasurementDisplay(), stretch=3)

        layoutLeftSide.addWidget(ConnectionPanel(), stretch=1)
        layoutLeftSide.addWidget(OscilloscopeConfigurePanel(), stretch=2)

        widget = QWidget()
        widget.setLayout(layoutWhole)
        self.setCentralWidget(widget)
