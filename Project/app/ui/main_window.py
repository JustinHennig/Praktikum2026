from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QStackedWidget, QVBoxLayout, QWidget, QApplication
from PySide6.QtCore import Qt

from app.services.device_functions import(
 auto_set, get_v_div, get_t_div, get_offset, get_trigger_level, set_amplitude, set_frequency, set_phase, 
 set_t_div, set_v_div, set_offset, set_offset_gen, set_trigger_level, set_waveform, set_output, get_output_status
)
from app.services.measurement_service import get_amplitude, get_frequency, get_pkpk, get_rms
from app.ui.components.measurement_display import MeasurementDisplay
from app.ui.components.device_configure_panels import FunctionGeneratorConfigurePanel, OscilloscopeConfigurePanel
from app.ui.components.connection_panel import ConnectionPanel
import datetime


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Measurement App for SCPI Instruments")
        self.setMinimumSize(1100, 700)

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
        self.oscilloscope_panel.auto_set_btn.clicked.connect(self.auto_set)
        self.oscilloscope_panel.scan_cur_set_btn.clicked.connect(self.scan_current_settings)
        self.oscilloscope_panel.save_set_btn.clicked.connect(self.set_settings)
        self.oscilloscope_panel.start_measurement_btn.clicked.connect(self.start_measurement)
        self.generator_panel.set_configuration_btn.clicked.connect(self.set_configuration)
        self.generator_panel.output_btn.clicked.connect(self.set_output)
        self.connection_panel.resource_combo.currentIndexChanged.connect(self.update_output_btn_status)
        self.generator_panel.channel_combo.currentIndexChanged.connect(self.update_output_btn_status)

        widget = QWidget()
        widget.setLayout(layoutWhole)
        self.setCentralWidget(widget)

    # Function to automatically set the oscilloscope settings based on the current resource
    def auto_set(self):
        resource = self.connection_panel.resource_combo.currentText()
        if not resource:
            return
        try:
            auto_set(resource)
        except Exception as e:
            print(f"Auto Set error: {e}")

    # Function to scan the current settings of the oscilloscope and update the input fields in the panel accordingly
    def scan_current_settings(self):
        resource = self.connection_panel.resource_combo.currentText()
        channel = int(self.oscilloscope_panel.channel_combo.currentText())

        if not resource:
            return
        try:
            self.oscilloscope_panel.v_div_input.setText(get_v_div(resource, channel))
            self.oscilloscope_panel.t_div_input.setText(get_t_div(resource))
            self.oscilloscope_panel.offset_input.setText(get_offset(resource, channel))
            self.oscilloscope_panel.trigger_input.setText(get_trigger_level(resource))
        except Exception as e:
            print(f"Scan settings error: {e}")

    # Function to set the oscilloscope settings based on the user input
    def set_settings(self):
        resource = self.connection_panel.resource_combo.currentText()
        channel = int(self.oscilloscope_panel.channel_combo.currentText())

        if not resource:
            return
        try:
            set_v_div(resource, float(self.oscilloscope_panel.v_div_input.text()), channel)
            set_t_div(resource, float(self.oscilloscope_panel.t_div_input.text()))
            set_offset(resource, float(self.oscilloscope_panel.offset_input.text()), channel)
            set_trigger_level(resource, float(self.oscilloscope_panel.trigger_input.text()))
        except Exception as e:
            print(f"Set settings error: {e}")

    # Function to start the measurement
    def start_measurement(self):
        resource = self.connection_panel.resource_combo.currentText()
        channel = int(self.oscilloscope_panel.channel_combo.currentText())
        measurement_type = self.oscilloscope_panel.type_combo.currentText()

        if not resource:
            return

        # Depending on the measurement type, either take a single measurement or continuously measure for a period of time
        if measurement_type == "Period of time":
            try:
                length = float(self.oscilloscope_panel.pot_length_input.text())
                measurements_per_s = float(self.oscilloscope_panel.pot_measurement_s_input.text())
                interval = 1.0 / measurements_per_s if measurements_per_s > 0 else 1.0
                num_measurements = int(length * measurements_per_s)
                for i in range(num_measurements):
                    frequency = get_frequency(resource)
                    amplitude = get_amplitude(resource, channel)
                    pkpk = get_pkpk(resource, channel)
                    rms = get_rms(resource, channel)
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    self.oscilloscope_panel.frequency_label.setText(frequency)
                    self.oscilloscope_panel.amplitude_label.setText(amplitude)
                    self.oscilloscope_panel.pkpk_label.setText(pkpk)
                    self.oscilloscope_panel.rms_label.setText(rms)

                    measurement_data = {
                        "Resource": resource,
                        "Channel": channel,
                        "Time": timestamp,
                        "Frequency": frequency,
                        "Amplitude": amplitude,
                        "Peak-to-Peak": pkpk,
                        "RMS": rms,
                        "v_div_mv": get_v_div(resource, channel),
                        "t_div_ms": get_t_div(resource),
                        "offset_mv": get_offset(resource, channel),
                        "trigger_level": get_trigger_level(resource)
                    }
                    self.measurement_display.add_measurement(measurement_data)
                    QApplication.processEvents()
                    import time
                    time.sleep(interval)
            except Exception as e:
                print(f"Period of time measurement error: {e}")
        else:
            try:
                frequency = get_frequency(resource)
                amplitude = get_amplitude(resource, channel)
                pkpk = get_pkpk(resource, channel)
                rms = get_rms(resource, channel)
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                self.oscilloscope_panel.frequency_label.setText(frequency)
                self.oscilloscope_panel.amplitude_label.setText(amplitude)
                self.oscilloscope_panel.pkpk_label.setText(pkpk)
                self.oscilloscope_panel.rms_label.setText(rms)

                measurement_data = {
                    "Resource": resource,
                    "Channel": channel,
                    "Time": timestamp,
                    "Frequency": frequency,
                    "Amplitude": amplitude,
                    "Peak-to-Peak": pkpk,
                    "RMS": rms,
                    "v_div_mv": get_v_div(resource, channel),
                    "t_div_ms": get_t_div(resource),
                    "offset_mv": get_offset(resource, channel),
                    "trigger_level": get_trigger_level(resource)
                }
                self.measurement_display.add_measurement(measurement_data)
            except Exception as e:
                print(f"Start measurement error: {e}")

    # Function to set the configuration of the generator based on user input
    def set_configuration(self):
        resource = self.connection_panel.resource_combo.currentText()
        channel = int(self.generator_panel.channel_combo.currentText())

        if not resource:
            return
        try:
            set_waveform(resource, self.generator_panel.waveform_combo.currentText(), channel)
            set_frequency(resource, float(self.generator_panel.frequency_input.text()), channel)
            set_amplitude(resource, float(self.generator_panel.amplitude_input.text()), channel)
            set_offset_gen(resource, float(self.generator_panel.offset_input.text()), channel)
            set_phase(resource, float(self.generator_panel.phase_input.text()), channel)
        except Exception as e:
            print(f"Set configuration error: {e}")

    # Function to toggle the output of the generator on and off
    def set_output(self):
        resource = self.connection_panel.resource_combo.currentText()
        channel = int(self.generator_panel.channel_combo.currentText())
        btn = self.generator_panel.output_btn

        if not resource:
            return
        try:
            new_status = set_output(resource, channel)
            btn.setText(f"Output: {new_status}")
        except Exception as e:
            print(f"Set output error: {e}")

    # Function to update the output button of the generator
    def update_output_btn_status(self):
        resource = self.connection_panel.resource_combo.currentText()
        channel = int(self.generator_panel.channel_combo.currentText())
        btn = self.generator_panel.output_btn
        if not resource:
            btn.setText("Output: OFF")
            return
        try:
            status = get_output_status(resource, channel)
            btn.setText(f"Output: {status}")
        except Exception:
            btn.setText("Output: OFF")

