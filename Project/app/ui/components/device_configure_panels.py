# This file contains the OscilloscopeConfigurePanel and FunctionGeneratorConfigurePanel classes,
# Which are used in the main window to display the configuration options for the oscilloscope and function generator

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QGroupBox, QHBoxLayout, QLabel, QPushButton, QSlider,
    QVBoxLayout, QComboBox, QLineEdit, QWidget
)
import math

# Panel for configuring the oscilloscope settings and measurement parameters
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

        # Oscilloscope configuration settings
        settings_layout = QVBoxLayout()
        settings_layout.addWidget(QLabel("Configuration Settings:"))

        v_div_row = QHBoxLayout()
        v_div_row.addWidget(QLabel("V/div:"))
        self.v_div_input = QLineEdit()
        v_div_row.addWidget(self.v_div_input)
        v_div_row.addWidget(QLabel("mV"))

        us_div_row = QHBoxLayout()
        us_div_row.addWidget(QLabel("T/div:"))
        self.t_div_input = QLineEdit()
        us_div_row.addWidget(self.t_div_input)
        us_div_row.addWidget(QLabel("ms"))

        offset_row = QHBoxLayout()
        offset_row.addWidget(QLabel("Offset:"))
        self.offset_input = QLineEdit()
        offset_row.addWidget(self.offset_input)
        offset_row.addWidget(QLabel("mV"))

        trigger_row = QHBoxLayout()
        trigger_row.addWidget(QLabel("Trigger Level:"))
        self.trigger_input = QLineEdit()
        trigger_row.addWidget(self.trigger_input)
        trigger_row.addWidget(QLabel("mV"))

        btn_row = QHBoxLayout()
        self.scan_cur_set_btn = QPushButton("Scan Current Settings")
        self.auto_set_btn = QPushButton("Auto Set")
        self.save_set_btn = QPushButton("Set Settings")
        btn_row.addWidget(self.scan_cur_set_btn)
        btn_row.addWidget(self.auto_set_btn)
        btn_row.addWidget(self.save_set_btn)


        settings_layout.addLayout(v_div_row)
        settings_layout.addLayout(us_div_row)
        settings_layout.addLayout(offset_row)
        settings_layout.addLayout(trigger_row)
        settings_layout.addLayout(btn_row)
        layout.addLayout(settings_layout)


        # Mode selector row (label switches between "Snapshot configuration" and "Measurement Parameters")
        mode_row = QHBoxLayout()
        self.mode_label = QLabel("Snapshot configuration:")
        mode_row.addWidget(self.mode_label)
        self.parameter_combo = QComboBox()
        self.parameter_combo.setEditable(False)
        self.parameter_combo.addItems(["Snapshot", "Live Measurement"])
        mode_row.addWidget(self.parameter_combo)
        layout.addLayout(mode_row)

        # Snapshot configuration widget
        self.snapshot_widget = QWidget()
        snapshot_layout = QVBoxLayout(self.snapshot_widget)
        snapshot_layout.setContentsMargins(0, 0, 0, 0)

        # Number of points, logarithmic slider + input field
        points_row = QHBoxLayout()
        points_row.addWidget(QLabel("Points (log. scale):"))
        self.snapshot_points_slider = QSlider(Qt.Orientation.Horizontal)
        self.snapshot_points_slider.setMinimum(0)
        self.snapshot_points_slider.setMaximum(100)
        self.snapshot_points_slider.setValue(100)
        points_row.addWidget(self.snapshot_points_slider)
        self.snapshot_points_input = QLineEdit("1250000")
        self.snapshot_points_input.setFixedWidth(80)
        self.snapshot_points_input.setToolTip("Number of waveform points to transfer")
        points_row.addWidget(self.snapshot_points_input)
        snapshot_layout.addLayout(points_row)

        # Filename
        filename_row = QHBoxLayout()
        filename_row.addWidget(QLabel("Filename:"))
        self.snapshot_filename_input = QLineEdit("snapshot_C1")
        filename_row.addWidget(self.snapshot_filename_input)
        snapshot_layout.addLayout(filename_row)

        # Smoothing
        smoothing_row = QHBoxLayout()
        smoothing_row.addWidget(QLabel("Smoothing:"))
        self.snapshot_smoothing_combo = QComboBox()
        self.snapshot_smoothing_combo.addItems(["None", "Moving Average", "Savitzky-Golay"])
        smoothing_row.addWidget(self.snapshot_smoothing_combo)
        snapshot_layout.addLayout(smoothing_row)

        layout.addWidget(self.snapshot_widget)

        # Measurement parameters widget (Live Measurement)
        self.live_widget = QWidget()
        parameter_layout = QVBoxLayout(self.live_widget)
        parameter_layout.setContentsMargins(0, 0, 0, 0)
        self.live_widget.setVisible(False)

        # Parameters for a live measurement
        frequency_row = QHBoxLayout()
        self.frequency_checkbox = QCheckBox()
        self.frequency_checkbox.setChecked(True)
        frequency_row.addWidget(self.frequency_checkbox)
        frequency_row.addWidget(QLabel("Frequency:"))
        self.frequency_label = QLabel("—")
        frequency_row.addWidget(self.frequency_label)
        frequency_row.addWidget(QLabel("Hz"))

        amplitude_row = QHBoxLayout()
        self.amplitude_checkbox = QCheckBox()
        self.amplitude_checkbox.setChecked(True)
        amplitude_row.addWidget(self.amplitude_checkbox)
        amplitude_row.addWidget(QLabel("Amplitude:"))
        self.amplitude_label = QLabel("—")
        amplitude_row.addWidget(self.amplitude_label)
        amplitude_row.addWidget(QLabel("V"))

        pkpk_row = QHBoxLayout()
        self.pkpk_checkbox = QCheckBox()
        self.pkpk_checkbox.setChecked(True)
        pkpk_row.addWidget(self.pkpk_checkbox)
        pkpk_row.addWidget(QLabel("Peak-to-Peak:"))
        self.pkpk_label = QLabel("—")
        pkpk_row.addWidget(self.pkpk_label)
        pkpk_row.addWidget(QLabel("V"))

        rms_row = QHBoxLayout()
        self.rms_checkbox = QCheckBox()
        self.rms_checkbox.setChecked(True)
        rms_row.addWidget(self.rms_checkbox)
        rms_row.addWidget(QLabel("RMS:"))
        self.rms_label = QLabel("—")
        rms_row.addWidget(self.rms_label)
        rms_row.addWidget(QLabel("V"))

        parameter_layout.addLayout(frequency_row)
        parameter_layout.addLayout(amplitude_row)
        parameter_layout.addLayout(pkpk_row)
        parameter_layout.addLayout(rms_row)

        # Measurement name
        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("Measurement Name:"))
        self.measurement_name_input = QLineEdit()
        name_row.addWidget(self.measurement_name_input)
        parameter_layout.addLayout(name_row)

        # Measurement Type
        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Measurement Type:"))
        self.type_combo = QComboBox()
        self.type_combo.setEditable(False)
        self.type_combo.addItems(["Single", "Period of time", "Sweep"])
        type_row.addWidget(self.type_combo)
        parameter_layout.addLayout(type_row)

        # Period of time settings
        self.pot_widget = QWidget()
        pot_row = QHBoxLayout()
        pot_row.addWidget(QLabel("Length (s): "))
        self.pot_length_input = QLineEdit()
        pot_row.addWidget(self.pot_length_input)
        pot_row.addWidget(QLabel("Measurements/s: "))
        self.pot_measurement_s_input = QLineEdit()
        pot_row.addWidget(self.pot_measurement_s_input)
        pot_row.setContentsMargins(0, 0, 0, 0)
        self.pot_widget.setLayout(pot_row)
        parameter_layout.addWidget(self.pot_widget)
        self.pot_widget.setVisible(False)

        # Sweep settings
        self.sweep_widget = QWidget()
        sweep_row = QHBoxLayout()
        sweep_row.addWidget(QLabel("Start Freq(Hz): "))
        self.sweep_start_input = QLineEdit()
        sweep_row.addWidget(self.sweep_start_input)
        sweep_row.addWidget(QLabel("Stop Freq(Hz): "))
        self.sweep_stop_input = QLineEdit()
        sweep_row.addWidget(self.sweep_stop_input)
        sweep_row.addWidget(QLabel("Points: "))
        self.sweep_points_input = QLineEdit()
        sweep_row.addWidget(self.sweep_points_input)
        sweep_row.setContentsMargins(0, 0, 0, 0)
        self.sweep_widget.setLayout(sweep_row)
        parameter_layout.addWidget(self.sweep_widget)
        self.sweep_widget.setVisible(False)

        layout.addWidget(self.live_widget)


        # Measurement buttons
        measurement_btn_row = QHBoxLayout()
        self.start_measurement_btn = QPushButton("Start Measurement")
        self.stop_btn = QPushButton("Cancel")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setVisible(False)
        measurement_btn_row.addWidget(self.start_measurement_btn)
        measurement_btn_row.addWidget(self.stop_btn)
        layout.addLayout(measurement_btn_row)

        #Signals
        self.type_combo.currentIndexChanged.connect(self.update_pot_visibility)
        self.parameter_combo.currentIndexChanged.connect(self.update_mode_visibility)
        self.snapshot_points_slider.valueChanged.connect(self.slider_to_input)
        self.snapshot_points_input.editingFinished.connect(self.input_to_slider)


    # Logarthmic slider funtions
    POINTS_MIN = 10
    POINTS_MAX = 1_250_000

    def slider_to_points(self, slider_val: int) -> int:
        log_min = math.log10(self.POINTS_MIN)
        log_max = math.log10(self.POINTS_MAX)
        return round(10 ** (log_min + slider_val / 100 * (log_max - log_min)))

    def points_to_slider(self, points: int) -> int:
        points = max(self.POINTS_MIN, min(self.POINTS_MAX, points))
        log_min = math.log10(self.POINTS_MIN)
        log_max = math.log10(self.POINTS_MAX)
        return round((math.log10(points) - log_min) / (log_max - log_min) * 100)

    def slider_to_input(self, slider_val: int):
        self.snapshot_points_input.setText(str(self.slider_to_points(slider_val)))

    def input_to_slider(self):
        try:
            points = int(self.snapshot_points_input.text())
        except ValueError:
            return
        self.snapshot_points_slider.blockSignals(True)
        self.snapshot_points_slider.setValue(self.points_to_slider(points))
        self.snapshot_points_slider.blockSignals(False)

    # Update visibility of snapshot/live measurement settings based on mode selection
    def update_mode_visibility(self):
        is_snapshot = self.parameter_combo.currentText() == "Snapshot"
        self.snapshot_widget.setVisible(is_snapshot)
        self.live_widget.setVisible(not is_snapshot)
        self.mode_label.setText("Snapshot configuration:" if is_snapshot else "Measurement Parameters:")

    # Update visibility of period of time and sweep settings based on measurement type selection
    def update_pot_visibility(self):
        selected = self.type_combo.currentText()
        self.pot_widget.setVisible(selected == "Period of time")
        self.sweep_widget.setVisible(selected == "Sweep")
        self.stop_btn.setVisible(selected != "Single")

# Panel for configuring the function generator settings
class FunctionGeneratorConfigurePanel(QGroupBox):
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

        # Waveform configuration
        waveform_row = QHBoxLayout()
        waveform_row.addWidget(QLabel("Waveform:"))
        self.waveform_combo = QComboBox()
        self.waveform_combo.setEditable(False)
        self.waveform_combo.addItems(["Sine", "Square", "Ramp", "Pulse", "Noise", "DC", "Arb"])
        waveform_row.addWidget(self.waveform_combo)
        layout.addLayout(waveform_row)

        # Frequency configuration
        frequency_row = QHBoxLayout()
        frequency_row.addWidget(QLabel("Frequency:"))
        self.frequency_input = QLineEdit()
        frequency_row.addWidget(self.frequency_input)
        frequency_row.addWidget(QLabel("Hz"))
        layout.addLayout(frequency_row)

        # Amplitude configuration
        amplitude_row = QHBoxLayout()
        amplitude_row.addWidget(QLabel("Amplitude:"))
        self.amplitude_input = QLineEdit()
        amplitude_row.addWidget(self.amplitude_input)
        amplitude_row.addWidget(QLabel("Vpp"))
        layout.addLayout(amplitude_row)

        # Offset configuration
        offset_row = QHBoxLayout()
        offset_row.addWidget(QLabel("Offset:"))
        self.offset_input = QLineEdit()
        offset_row.addWidget(self.offset_input)
        offset_row.addWidget(QLabel("Vdc"))
        layout.addLayout(offset_row)

        # Phase configuration
        phase_row = QHBoxLayout()
        phase_row.addWidget(QLabel("Phase:"))
        self.phase_input = QLineEdit()
        phase_row.addWidget(self.phase_input)
        phase_row.addWidget(QLabel("°"))
        layout.addLayout(phase_row)

        # Button row
        button_row = QHBoxLayout()
        self.set_configuration_btn = QPushButton("Set configuration")
        self.save_configuration_btn = QPushButton("Save configuration")
        self.output_btn = QPushButton("Output: OFF")

        button_row.addWidget(self.set_configuration_btn)
        button_row.addWidget(self.save_configuration_btn)
        button_row.addWidget(self.output_btn)
        layout.addLayout(button_row)

