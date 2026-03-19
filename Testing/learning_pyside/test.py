import sys
import time
import traceback

from PySide6.QtCore import QTimer, QRunnable, Slot, QThread, Signal, QObject
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QProgressBar
)

class Worker(QObject):
    progress = Signal(int)
    completed = Signal(int)

    @Slot(int)
    def do_work(self, n):
        for i in range(1, n + 1):
            time.sleep(1)
            self.progress.emit(i)
        self.completed.emit(i)

class MainWindow(QMainWindow):
    work_requested = Signal(int)

    def __init__(self):
        super().__init__()

        self.setGeometry(100, 100, 300, 50)
        self.setWindowTitle("Threading Example")

        #setup widget
        self.widget = QWidget()
        layout = QVBoxLayout()
        self.widget.setLayout(layout)
        self.setCentralWidget(self.widget)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)

        self.btn_start = QPushButton("Start Long Task", clicked=self.start)

        layout.addWidget(self.progress_bar)
        layout.addWidget(self.btn_start)

        self.worker = Worker()
        self.worker_thread = QThread()

        self.worker.progress.connect(self.update_progress)
        self.worker.completed.connect(self.complete)

        self.work_requested.connect(self.worker.do_work)

        # move worker to the worker thread
        self.worker.moveToThread(self.worker_thread)

        # start thread
        self.worker_thread.start()

        self.show()

    def start(self):
        self.btn_start.setEnabled(False)
        n = 5
        self.progress_bar.setMaximum(n)
        self.work_requested.emit(n)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def complete(self, value):
        self.progress_bar.setValue(value)
        self.btn_start.setEnabled(True)

app = QApplication([])
window = MainWindow()
app.exec()