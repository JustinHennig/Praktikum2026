# This file contains the DeviceWorker class, which is responsible for running device communication in a separate thread to keep the UI responsive.

import queue
from PySide6.QtCore import QObject, Signal


class DeviceWorker(QObject):
    result_ready = Signal(str, object)  # (task_id, result)
    error_occurred = Signal(str, str)   # (task_id, error_message)

    def __init__(self):
        super().__init__()
        self._queue: queue.Queue = queue.Queue()

    # Method to submit a task to the worker thread
    def submit(self, task_id: str, func, *args, **kwargs):
        self._queue.put((task_id, func, args, kwargs))

    # Main loop of the worker thread, which processes tasks from the queue
    def run(self):
        while True:
            task_id, func, args, kwargs = self._queue.get()
            if task_id is None:
                break
            try:
                result = func(*args, **kwargs)
                self.result_ready.emit(task_id, result)
            except Exception as e:
                self.error_occurred.emit(task_id, str(e))

    # Method to stop the worker thread (not cancel ongoing tasks, but prevents new tasks from being processed)
    def stop(self):
        self._queue.put((None, None, (), {}))