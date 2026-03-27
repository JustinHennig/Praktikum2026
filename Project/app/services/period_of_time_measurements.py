# This file contains the PeriodOfTimeMeasurement class, which is responsible for performing measurements over a specified period of time.

from PySide6.QtCore import QObject, QTimer, Signal

class PeriodOfTimeMeasurement(QObject):
    tick = Signal(str, int, bool, bool, bool, bool)
    finished = Signal()

    # Initializes the object, sets up the timer and connects the timeout signal to the on_tick method.
    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_tick)
        self.remaining = 0
        self.resource = ""
        self.channel = 0
        self.checkboxes = (False, False, False, False)

    # Handles the starting of the measurement process
    def start(self, resource: str, channel: int, length: float, measurements_per_s: float, checkboxes: tuple[bool, bool, bool, bool]):
        interval_ms = int(1000 / measurements_per_s) if measurements_per_s > 0 else 1000
        self.remaining = int(length * measurements_per_s)
        self.resource = resource
        self.channel = channel
        self.checkboxes = checkboxes
        self.timer.start(interval_ms)

    # Method to stop the measurement process and emit the finished signal
    def stop(self):
        self.timer.stop()
        self.finished.emit()

    # Timer tick handler, emits the tick signal with the current resource, channel, and checkbox states, and decrements the remaining measurement count
    def _on_tick(self):
        if self.remaining <= 0:
            self.stop()
            return
        self.tick.emit(self.resource, self.channel, *self.checkboxes)
        self.remaining -= 1