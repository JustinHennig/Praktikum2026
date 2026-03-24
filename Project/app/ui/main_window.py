# This file contains the MainWindow class, which is the main window of the application and contains
# all the different panels splitted into a left and right side
# while the left side contains the connection panel and the configuration panels for the oscilloscope and function generator.
# The right side contains the measurement display

from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QMessageBox, QStackedWidget, QVBoxLayout, QWidget
from PySide6.QtCore import QThread, QTimer
from app.services.device_worker import DeviceWorker
from app.scpi_commands.sds_commands import(
 auto_set, get_v_div, get_t_div, get_offset, get_trigger_level, get_amplitude, get_frequency, get_pkpk, get_rms,
 set_t_div, set_v_div, set_offset, set_trigger_level, collect_measurement
)
from app.scpi_commands.sdg_commands import set_waveform, set_frequency, set_amplitude, set_offset_gen, set_phase, set_output, get_output_status
from app.ui.components.measurement_display import MeasurementDisplay
from app.ui.components.device_configure_panels import FunctionGeneratorConfigurePanel, OscilloscopeConfigurePanel
from app.ui.components.connection_panel import ConnectionPanel
import datetime


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Measurement App for SCPI Instruments")
        self.setMinimumSize(1100, 700)

        # Device Workers
        self._sds_worker = DeviceWorker()
        self._sds_thread = QThread(self)
        self._sds_worker.moveToThread(self._sds_thread)
        self._sds_thread.started.connect(self._sds_worker.run)
        self._sds_worker.result_ready.connect(self._on_sds_result)
        self._sds_worker.error_occurred.connect(self._on_device_error)
        self._sds_thread.start()

        self._sdg_worker = DeviceWorker()
        self._sdg_thread = QThread(self)
        self._sdg_worker.moveToThread(self._sdg_thread)
        self._sdg_thread.started.connect(self._sdg_worker.run)
        self._sdg_worker.result_ready.connect(self._on_sdg_result)
        self._sdg_thread.start()

        # Layouts
        layoutWhole = QHBoxLayout()
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

        # Signals
        self.connection_panel.device_combo.currentIndexChanged.connect(self.config_stack.setCurrentIndex)
        self.connection_panel.resource_combo.currentIndexChanged.connect(self.update_output_btn_status)
        self.oscilloscope_panel.auto_set_btn.clicked.connect(self.auto_set)
        self.oscilloscope_panel.scan_cur_set_btn.clicked.connect(self.scan_current_settings)
        self.oscilloscope_panel.save_set_btn.clicked.connect(self.set_settings)
        self.oscilloscope_panel.start_measurement_btn.clicked.connect(self.start_measurement)
        self.generator_panel.set_configuration_btn.clicked.connect(self.set_configuration)
        self.generator_panel.save_configuration_btn.clicked.connect(self.save_configuration)
        self.generator_panel.output_btn.clicked.connect(self.set_output)
        self.generator_panel.channel_combo.currentIndexChanged.connect(self.update_output_btn_status)
        self.measurement_display.configuration_loaded.connect(self.load_configuration)
        self.oscilloscope_panel.measurement_name_input.textChanged.connect(self.measurement_display.set_measurement_name)

        # State for timed measurement loop
        self._measurement_timer = QTimer()
        self._measurement_timer.timeout.connect(self.on_measurement_tick)
        self._timer_remaining = 0
        self._timer_resource = ""
        self._timer_channel = 0

        widget = QWidget()
        widget.setLayout(layoutWhole)
        self.setCentralWidget(widget)

    # Function to automatically set the oscilloscope settings based on the current resource
    def auto_set(self):
        resource = self.connection_panel.resource_combo.currentText()
        if not resource:
            return
        self._sds_worker.submit("auto_set", auto_set, resource)

    # Function to scan the current settings of the oscilloscope and update the input fields in the panel accordingly
    def scan_current_settings(self):
        resource = self.connection_panel.resource_combo.currentText()
        channel = int(self.oscilloscope_panel.channel_combo.currentText())

        if not resource:
            return
        try:
            self._sds_worker.submit("v_div", get_v_div, resource, channel)
            self._sds_worker.submit("t_div", get_t_div, resource)
            self._sds_worker.submit("offset", get_offset, resource, channel)
            self._sds_worker.submit("trigger", get_trigger_level, resource)
        except Exception as e:
            print(f"Scan settings error: {e}")

    # Function to set the oscilloscope settings based on the user input
    def set_settings(self):
        resource = self.connection_panel.resource_combo.currentText()
        channel = int(self.oscilloscope_panel.channel_combo.currentText())

        if not resource:
            return
        try:
            self._sds_worker.submit("set_v_div", set_v_div, resource, float(self.oscilloscope_panel.v_div_input.text()), channel)
            self._sds_worker.submit("set_t_div", set_t_div, resource, float(self.oscilloscope_panel.t_div_input.text()))
            self._sds_worker.submit("set_offset", set_offset, resource, float(self.oscilloscope_panel.offset_input.text()), channel)
            self._sds_worker.submit("set_trigger", set_trigger_level, resource, float(self.oscilloscope_panel.trigger_input.text()))
        except Exception as e:
            print(f"Set settings error: {e}")

    # Reads checkbox state in the main thread and submits a full measurement to the SDS worker
    def submit_measurement(self, resource: str, channel: int):
        self._sds_worker.submit(
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
    def start_measurement(self):
        resource = self.connection_panel.resource_combo.currentText()
        channel = int(self.oscilloscope_panel.channel_combo.currentText())
        measurement_type = self.oscilloscope_panel.type_combo.currentText()

        if not resource:
            return
        
        confirm = QMessageBox.question(self, "Start Measurement", "Display needs to be cleared for a new measurement.", QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        if confirm != QMessageBox.StandardButton.Ok:
            return
        self.measurement_display.clear_display()

        # Depending on the measurement type, either take a single measurement or continuously measure for a period of time
        if measurement_type == "Period of time":
            try:
                length = float(self.oscilloscope_panel.pot_length_input.text())
                measurements_per_s = float(self.oscilloscope_panel.pot_measurement_s_input.text())
                interval_ms = int(1000 / measurements_per_s) if measurements_per_s > 0 else 1000
                self._timer_remaining = int(length * measurements_per_s)
                self._timer_resource = resource
                self._timer_channel = channel
                self.oscilloscope_panel.start_measurement_btn.setEnabled(False)
                self._measurement_timer.start(interval_ms)
            except Exception as e:
                print(f"Period of time measurement error: {e}")
        else:
            self.submit_measurement(resource, channel)

    # Function called on each tick of the measurement timer during a "Period of time" measurement, submits a measurement to the worker and stops the timer when the time is up
    def on_measurement_tick(self):
        if self._timer_remaining <= 0:
            self._measurement_timer.stop()
            self.oscilloscope_panel.start_measurement_btn.setEnabled(True)
            return
        self.submit_measurement(self._timer_resource, self._timer_channel)
        self._timer_remaining -= 1

    # Function to set the configuration of the generator based on user input
    def set_configuration(self):
        resource = self.connection_panel.resource_combo.currentText()
        channel = int(self.generator_panel.channel_combo.currentText())

        if not resource:
            return
        try:
            self._sdg_worker.submit("set_waveform", set_waveform, resource, self.generator_panel.waveform_combo.currentText(), channel)
            self._sdg_worker.submit("set_frequency", set_frequency, resource, float(self.generator_panel.frequency_input.text()), channel)
            self._sdg_worker.submit("set_amplitude", set_amplitude, resource, float(self.generator_panel.amplitude_input.text()), channel)
            self._sdg_worker.submit("set_offset_gen", set_offset_gen, resource, float(self.generator_panel.offset_input.text()), channel)
            self._sdg_worker.submit("set_phase", set_phase, resource, float(self.generator_panel.phase_input.text()), channel)
        except Exception as e:
            print(f"Set configuration error: {e}")

    # Function to save the current generator configuration to the table
    def save_configuration(self):
        resource = self.connection_panel.resource_combo.currentText()
        channel = int(self.generator_panel.channel_combo.currentText())

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
    def set_output(self):
        resource = self.connection_panel.resource_combo.currentText()
        channel = int(self.generator_panel.channel_combo.currentText())

        if not resource:
            return
        self._sdg_worker.submit("set_output", set_output, resource, channel)

    # Function to update the output button of the generator
    def update_output_btn_status(self):
        resource = self.connection_panel.resource_combo.currentText()
        channel = int(self.generator_panel.channel_combo.currentText())
        if not resource:
            self.generator_panel.output_btn.setText("Output: OFF")
            return
        self._sdg_worker.submit("output_status", get_output_status, resource, channel)

    # Function to load the configuration of the oscilloscope into the configuration panel
    def load_configuration(self, settings: dict):
        config = settings.get("configuration", {})

       # Determining is the device is a oscilloscope based on the presence of typical oscilloscope settings
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
                if result.get("Frequency") is not None:
                    self.oscilloscope_panel.frequency_label.setText(result["Frequency"])
                if result.get("Amplitude") is not None:
                    self.oscilloscope_panel.amplitude_label.setText(result["Amplitude"])
                if result.get("Peak-to-Peak") is not None:
                    self.oscilloscope_panel.pkpk_label.setText(result["Peak-to-Peak"])
                if result.get("RMS") is not None:
                    self.oscilloscope_panel.rms_label.setText(result["RMS"])
                self.measurement_display.add_measurement(result)

    # Handles results from the SDG generator worker
    def _on_sdg_result(self, task_id: str, result):
        match task_id:
            case "set_output" | "output_status":
                self.generator_panel.output_btn.setText(f"Output: {result}")

    # Handles errors from both device workers
    def _on_device_error(self, task_id: str, error: str):
        print(f"[{task_id}] Device error: {error}")
