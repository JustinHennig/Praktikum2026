from PySide6.QtWidgets import QGroupBox
from PySide6.QtGui import QPalette, QColor

class MeasurementDisplay(QGroupBox):
    def __init__(self):
        super().__init__("Measurement Display")
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("grey"))
        self.setPalette(palette)