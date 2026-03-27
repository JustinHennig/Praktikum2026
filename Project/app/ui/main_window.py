# This file contains the MainWindow class, which is the main window of the application and contains
# all the different panels splitted into a left and right side
# while the left side contains the connection panel and the configuration panels for the oscilloscope and function generator.
# The right side contains the measurement display

import os
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QMessageBox, QStackedWidget, QVBoxLayout, QWidget
from PySide6.QtCore import QThread
from PySide6.QtWidgets import QApplication
from app.services.sweep_measurement import run_sweep
from app.services.device_worker import DeviceWorker
from app.scpi_commands.sds_commands import(
 auto_set, get_v_div, get_t_div, get_offset, get_trigger_level,
 set_t_div, set_v_div, set_offset, set_trigger_level
)
from app.scpi_commands.sdg_commands import set_waveform, set_frequency, set_amplitude, set_offset_gen, set_phase, set_output, get_output_status
from app.services.single_measurement import collect_measurement
from app.ui.components.measurement_display import MeasurementDisplay
from app.ui.components.device_configure_panels import FunctionGeneratorConfigurePanel, OscilloscopeConfigurePanel
from app.ui.components.connection_panel import ConnectionPanel
from app.ui.components.header_panel import HeaderPanel
from app.services.period_of_time_measurements import PeriodOfTimeMeasurement
from app.services.snapshot import SnapshotService
import datetime

_STYLING_DIR = os.path.join(os.path.dirname(__file__), "styling")

def _load_qss(filename: str) -> str:
    path = os.path.join(_STYLING_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Measurement App for SCPI Instruments")
        self.setMinimumSize(1100, 800)

        # Device Workers
        self.sds_worker = DeviceWorker()
        self.sds_thread = QThread(self)
        self.sds_worker.moveToThread(self.sds_thread)
        self.sds_thread.started.connect(self.sds_worker.run)
        self.sds_worker.result_ready.connect(self._on_sds_result)
        self.sds_worker.error_occurred.connect(self._on_device_error)
        self.sds_thread.start()

        self.sdg_worker = DeviceWorker()
        self.sdg_thread = QThread(self)
        self.sdg_worker.moveToThread(self.sdg_thread)
        self.sdg_thread.started.connect(self.sdg_worker.run)
        self.sdg_worker.result_ready.connect(self._on_sdg_result)
        self.sdg_thread.start()

        # Layouts
        layoutRoot = QVBoxLayout()
        layoutRoot.setContentsMargins(0, 0, 0, 0)
        layoutRoot.setSpacing(0)

        # Header
        self.header = HeaderPanel()
        self.header.theme_changed.connect(self._apply_theme)
        layoutRoot.addWidget(self.header)

        layoutWhole = QHBoxLayout()
        layoutWhole.setContentsMargins(8, 8, 8, 8)
        layoutWhole.setSpacing(8)
        layoutLeftSide = QVBoxLayout()

        # Connection Panel
        self.connection_panel = ConnectionPanel()
        layoutLeftSide.addWidget(self.connection_panel, stretch=2)

        # Stacked widget for changing the configuration panel based on the selected device type
        self.config_stack = QStackedWidget()
        self.oscilloscope_panel = OscilloscopeConfigurePanel()
        self.generator_panel = FunctionGeneratorConfigurePanel()
        self.config_stack.addWidget(self.oscilloscope_panel)
        self.config_stack.addWidget(self.generator_panel)
        layoutLeftSide.addWidget(self.config_stack, stretch=5)

        # Measurement Display
        self.measurement_display = MeasurementDisplay()
        layoutWhole.addLayout(layoutLeftSide, stretch=2)
        layoutWhole.addWidget(self.measurement_display, stretch=3)
        layoutRoot.addLayout(layoutWhole)

        # Signals
        self.connection_panel.device_combo.currentIndexChanged.connect(self.config_stack.setCurrentIndex)
        self.connection_panel.gen_resource_combo.currentIndexChanged.connect(self._update_output_btn_status)
        self.oscilloscope_panel.auto_set_btn.clicked.connect(self._auto_set)
        self.oscilloscope_panel.scan_cur_set_btn.clicked.connect(self._scan_current_settings)
        self.oscilloscope_panel.save_set_btn.clicked.connect(self._set_settings)
        self.oscilloscope_panel.start_measurement_btn.clicked.connect(self._start_measurement)
        self.oscilloscope_panel.stop_btn.clicked.connect(self._stop_measurement)
        self.generator_panel.set_configuration_btn.clicked.connect(self._set_configuration)
        self.generator_panel.save_configuration_btn.clicked.connect(self._save_configuration)
        self.generator_panel.output_btn.clicked.connect(self._set_output)
        self.generator_panel.channel_combo.currentIndexChanged.connect(self._update_output_btn_status)
        self.measurement_display.configuration_loaded.connect(self._load_configuration)
        self.oscilloscope_panel.measurement_name_input.textChanged.connect(self.measurement_display.set_measurement_name)

        # State for timed measurement loop
        self.pot_measurement = PeriodOfTimeMeasurement()
        self.pot_measurement.tick.connect(self._on_pot_tick)
        self.pot_measurement.finished.connect(self._on_pot_finished)
        self._measurement_start: datetime.datetime | None = None

        # Snapshot service
        self.snapshot_service = SnapshotService()
        self.snapshot_service.finished.connect(self._on_snapshot_finished)
        self.snapshot_service.error.connect(self._on_snapshot_error)

        widget = QWidget()
        widget.setLayout(layoutRoot)
        self.setCentralWidget(widget)

    # ── Theme helpers ──────────────────────────────
    def _apply_theme(self, is_light: bool):
        qss = _load_qss("theme_light.qss" if is_light else "theme_dark.qss")
        app = QApplication.instance()
        if isinstance(app, QApplication):
            app.setStyleSheet(qss)

    # Properties for quick access to the current resource and channel
    @property
    def current_osc_resource(self) -> str:
        return self.connection_panel.osc_resource_combo.currentText()
    
    @property
    def current_osc_channel(self) -> int:
        return int(self.oscilloscope_panel.channel_combo.currentText())

    @property
    def current_gen_resource(self) -> str:
        return self.connection_panel.gen_resource_combo.currentText()

    @property
    def current_gen_channel(self) -> int:
        return int(self.generator_panel.channel_combo.currentText())

    # Function to automatically set the oscilloscope settings based on the current resource
    def _auto_set(self):
        resource = self.current_osc_resource
        if not resource:
            return
        self.sds_worker.submit("auto_set", auto_set, resource)

    # Function to scan the current settings of the oscilloscope and update the input fields in the panel accordingly
    def _scan_current_settings(self):
        resource = self.current_osc_resource
        channel = self.current_osc_channel

        if not resource:
            return
        try:
            self.sds_worker.submit("v_div", get_v_div, resource, channel)
            self.sds_worker.submit("t_div", get_t_div, resource)
            self.sds_worker.submit("offset", get_offset, resource, channel)
            self.sds_worker.submit("trigger", get_trigger_level, resource)
        except Exception as e:
            print(f"Scan settings error: {e}")

    # Function to set the oscilloscope settings based on the user input
    def _set_settings(self):
        resource = self.current_osc_resource
        channel = self.current_osc_channel

        if not resource:
            return
        try:
            self.sds_worker.submit("set_v_div", set_v_div, resource, float(self.oscilloscope_panel.v_div_input.text()), channel)
            self.sds_worker.submit("set_t_div", set_t_div, resource, float(self.oscilloscope_panel.t_div_input.text()))
            self.sds_worker.submit("set_offset", set_offset, resource, float(self.oscilloscope_panel.offset_input.text()), channel)
            self.sds_worker.submit("set_trigger", set_trigger_level, resource, float(self.oscilloscope_panel.trigger_input.text()))
        except Exception as e:
            print(f"Set settings error: {e}")

    # Reads checkbox state in the main thread and submits a full measurement to the SDS worker
    def _submit_measurement(self, resource: str, channel: int):
        self.sds_worker.submit(
            "measurement",
            collect_measurement,
            resource,
            channel,
            self.oscilloscope_panel.frequency_checkbox.isChecked(),
            self.oscilloscope_panel.amplitude_checkbox.isChecked(),
            self.oscilloscope_panel.pkpk_checkbox.isChecked(),
            self.oscilloscope_panel.rms_checkbox.isChecked(),
        )

    # Function to start the measurement
    def _start_measurement(self):
        resource = self.current_osc_resource
        channel  = self.current_osc_channel

        if not resource:
            return

        # Snapshot mode
        if self.oscilloscope_panel.parameter_combo.currentText() == 'Snapshot':
            points   = int(self.oscilloscope_panel.snapshot_points_input.text())
            filename = self.oscilloscope_panel.snapshot_filename_input.text() or 'snapshot'
            smoothing = self.oscilloscope_panel.snapshot_smoothing_combo.currentText()
            self.oscilloscope_panel.start_measurement_btn.setEnabled(False)
            self.sds_worker.submit('snapshot', self.snapshot_service.run, resource, channel, points, filename, smoothing)
            return

        measurement_type = self.oscilloscope_panel.type_combo.currentText()

        # If the display already has data, add a separator row for the new setting;
        # otherwise start with a clean display
        real_data = [d for d in self.measurement_display.measurement_data if "__separator__" not in d]
        if real_data:
            label = f"New Setting  —  Ch {channel}  |  {measurement_type}"
            self.measurement_display.add_separator(label)
        else:
            self.measurement_display.clear_display()

        self._measurement_start = datetime.datetime.now()

        # Depending on the measurement type, either take a single measurement or continuously measure for a period of time
        if measurement_type == "Period of time":
            try:
                length = float(self.oscilloscope_panel.pot_length_input.text())
                measurements_per_s = float(self.oscilloscope_panel.pot_measurement_s_input.text())
                self.oscilloscope_panel.start_measurement_btn.setEnabled(False)
                self.oscilloscope_panel.stop_btn.setEnabled(True)
                self.pot_measurement.start(
                    resource, channel, length, measurements_per_s,
                    (
                        self.oscilloscope_panel.frequency_checkbox.isChecked(),
                        self.oscilloscope_panel.amplitude_checkbox.isChecked(),
                        self.oscilloscope_panel.pkpk_checkbox.isChecked(),
                        self.oscilloscope_panel.rms_checkbox.isChecked(),
                    )
                )
            except Exception as e:
                print(f"Period of time measurement error: {e}")
        elif measurement_type == "Single":
            self._submit_measurement(resource, channel)
        elif measurement_type == "Sweep":
            try:
                start_freq = float(self.oscilloscope_panel.sweep_start_input.text())
                stop_freq  = float(self.oscilloscope_panel.sweep_stop_input.text())
                points     = int(self.oscilloscope_panel.sweep_points_input.text())
                self.sds_worker.submit(
                    "sweep",
                    run_sweep,
                    self.current_gen_resource,
                    self.current_osc_resource,
                    self.current_gen_channel,
                    self.current_osc_channel,
                    start_freq, stop_freq, points,
                )
                self.oscilloscope_panel.start_measurement_btn.setEnabled(False)
            except Exception as e:
                print(f"Sweep error: {e}")

    def _stop_measurement(self):
        self.pot_measurement.stop()

    # Function called on each tick of the measurement timer during a "Period of time" measurement, submits a measurement to the worker and stops the timer when the time is up
    def _on_pot_tick(self, resource, channel, freq, amp, pkpk, rms):
        self.sds_worker.submit("measurement", collect_measurement, resource, channel, freq, amp, pkpk, rms)

    def _on_pot_finished(self):
        self.oscilloscope_panel.start_measurement_btn.setEnabled(True)
        self.oscilloscope_panel.stop_btn.setEnabled(False)

    # Function to set the configuration of the generator based on user input
    def _set_configuration(self):
        resource = self.current_gen_resource
        channel = self.current_gen_channel

        if not resource:
            return
        try:
            self.sdg_worker.submit("set_waveform", set_waveform, resource, self.generator_panel.waveform_combo.currentText(), channel)
            self.sdg_worker.submit("set_frequency", set_frequency, resource, float(self.generator_panel.frequency_input.text()), channel)
            self.sdg_worker.submit("set_amplitude", set_amplitude, resource, float(self.generator_panel.amplitude_input.text()), channel)
            self.sdg_worker.submit("set_offset_gen", set_offset_gen, resource, float(self.generator_panel.offset_input.text()), channel)
            self.sdg_worker.submit("set_phase", set_phase, resource, float(self.generator_panel.phase_input.text()), channel)
        except Exception as e:
            QMessageBox.warning(self, "Set Configuration Error", f"An error occurred while setting the configuration:\n{e}")

    # Function to save the current generator configuration to the table
    def _save_configuration(self):
        resource = self.current_gen_resource
        channel = self.current_gen_channel

        try:
            config_data = {
                "Resource": resource,
                "Channel": channel,
                "Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Waveform":  self.generator_panel.waveform_combo.currentText(),
                "Frequency": self.generator_panel.frequency_input.text(),
                "Amplitude": self.generator_panel.amplitude_input.text(),
                "Offset":    self.generator_panel.offset_input.text(),
                "Phase":     self.generator_panel.phase_input.text(),
            }
            self.measurement_display.add_measurement(config_data)
        except Exception as e:
            print(f"Save configuration error: {e}")

    # Function to toggle the output of the generator on and off
    def _set_output(self):
        resource = self.current_gen_resource
        channel = self.current_gen_channel

        if not resource:
            return
        self.sdg_worker.submit("set_output", set_output, resource, channel)

    # Function to update the output button of the generator
    def _update_output_btn_status(self):
        resource = self.current_gen_resource
        channel = self.current_gen_channel
        if not resource:
            self.generator_panel.output_btn.setText("Output: OFF")
            return
        self.sdg_worker.submit("output_status", get_output_status, resource, channel)

    # Function to load the configuration of the oscilloscope into the configuration panel
    def _load_configuration(self, settings: dict):
        config = settings.get("configuration", {})

        # Determining if the device is a oscilloscope based on the presence of typical oscilloscope settings
        if any(k in config for k in ["v_div_mv", "t_div_ms", "offset_mv", "trigger_level"]):
            self.connection_panel.device_combo.setCurrentIndex(0)
            self.config_stack.setCurrentIndex(0)
        
        # If the configuration contains a channel setting, set the channel combo box in both panels to that channel
        if "Channel" in config:
            self.oscilloscope_panel.channel_combo.setCurrentText(str(config["Channel"]))
            self.generator_panel.channel_combo.setCurrentText(str(config["Channel"]))
        if "v_div_mv" in config:
            self.oscilloscope_panel.v_div_input.setText(str(config["v_div_mv"]))
        if "t_div_ms" in config:
            self.oscilloscope_panel.t_div_input.setText(str(config["t_div_ms"]))
        if "offset_mv" in config:
            self.oscilloscope_panel.offset_input.setText(str(config["offset_mv"]))
        if "trigger_level" in config:
            self.oscilloscope_panel.trigger_input.setText(str(config["trigger_level"]))

        if settings.get("name"):
            self.oscilloscope_panel.measurement_name_input.setText(settings["name"])

    # Handles results from the SDS oscilloscope worker
    def _on_sds_result(self, task_id: str, result):
        match task_id:
            case "v_div":
                self.oscilloscope_panel.v_div_input.setText(result)
            case "t_div":
                self.oscilloscope_panel.t_div_input.setText(result)
            case "offset":
                self.oscilloscope_panel.offset_input.setText(result)
            case "trigger":
                self.oscilloscope_panel.trigger_input.setText(result)
            case "measurement":
                elapsed = (
                    (datetime.datetime.now() - self._measurement_start).total_seconds()
                    if self._measurement_start else 0.0
                )
                result["Elapsed_Time"] = f"{elapsed:g}"
                if result.get("Frequency") is not None:
                    self.oscilloscope_panel.frequency_label.setText(result["Frequency"])
                if result.get("Amplitude") is not None:
                    self.oscilloscope_panel.amplitude_label.setText(result["Amplitude"])
                if result.get("Peak-to-Peak") is not None:
                    self.oscilloscope_panel.pkpk_label.setText(result["Peak-to-Peak"])
                if result.get("RMS") is not None:
                    self.oscilloscope_panel.rms_label.setText(result["RMS"])
                self.measurement_display.add_measurement(result)
            case "sweep":
                sweep_start = self._measurement_start or datetime.datetime.now()
                for row in result:
                    elapsed = (datetime.datetime.now() - sweep_start).total_seconds()
                    row["Elapsed_Time"] = f"{elapsed:g}"
                    self.measurement_display.add_measurement(row)
                self.oscilloscope_panel.start_measurement_btn.setEnabled(True)
            case "snapshot":
                # result is None; finished/error signals handled separately
                pass

    # Handles results from the SDG generator worker
    def _on_sdg_result(self, task_id: str, result):
        match task_id:
            case "set_output" | "output_status":
                self.generator_panel.output_btn.setText(f"Output: {result}")

    # Handles errors from both device workers
    def _on_device_error(self, task_id: str, error: str):
        print(f"[{task_id}] Device error: {error}")

    def _on_snapshot_finished(self, path: str):
        self.oscilloscope_panel.start_measurement_btn.setEnabled(True)
        QMessageBox.information(self, "Snapshot", f"Snapshot saved: {path}")

    def _on_snapshot_error(self, error: str):
        self.oscilloscope_panel.start_measurement_btn.setEnabled(True)
        QMessageBox.critical(self, "Snapshot Error", f"An error occurred during snapshot: {error}")

    # Overwriting the close eveent of the main window to cleanly stop all worker threads when the application is closed
    def closeEvent(self, event):
        message = QMessageBox(self)
        message.setWindowTitle("Exit Application")
        message.setText("Are you sure you want to exit the application?")
        message.setInformativeText("All ongoing measurements will be stopped and unsaved data will be lost. (Ongoing operations will be stopped, but not cancelled, so there might be some delay until the application is fully closed)")
        message.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        message.setDefaultButton(QMessageBox.StandardButton.No)

        if message.exec() != QMessageBox.StandardButton.Yes:
            event.ignore()
            return

        self.pot_measurement.stop()

        # Stop all the worker threads cleanly
        self.sdg_worker.stop()
        self.sds_worker.stop()
        self.connection_panel.cleanup()

        # Block  until all threads have finished
        self.sdg_thread.quit()
        self.sdg_thread.wait()
        self.sds_thread.quit()
        self.sds_thread.wait()

        event.accept()
