from PySide6.QtWidgets import (
    QCheckBox, QGroupBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QComboBox, QLineEdit, QWidget
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

        #oscilloscope configuration settings
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

        buttons_row = QHBoxLayout()
        self.scan_cur_set_btn = QPushButton("Scan Current Settings")
        self.auto_set_btn = QPushButton("Auto Set")
        self.save_set_btn = QPushButton("Set Settings")
        buttons_row.addWidget(self.scan_cur_set_btn)
        buttons_row.addWidget(self.auto_set_btn)
        buttons_row.addWidget(self.save_set_btn)


        settings_layout.addLayout(v_div_row)
        settings_layout.addLayout(us_div_row)
        settings_layout.addLayout(offset_row)
        settings_layout.addLayout(trigger_row)
        settings_layout.addLayout(buttons_row)
        layout.addLayout(settings_layout)


        # measurement parameters
        parameter_layout = QVBoxLayout()
        parameter_layout.addWidget(QLabel("Measurement Parameters:"))

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
        layout.addLayout(parameter_layout)


        # Measurement Type
        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Measurement Type:"))
        self.type_combo = QComboBox()
        self.type_combo.setEditable(False)
        self.type_combo.addItems(["Single", "Period of time"])
        type_row.addWidget(self.type_combo)
        layout.addLayout(type_row)

        # Period of time settings
        self.pot_widget = QWidget()
        pot_row = QHBoxLayout()
        pot_row.addWidget(QLabel("Length (s): "))
        self.pot_length_input = QLineEdit()
        pot_row.addWidget(self.pot_length_input)
        pot_row.addWidget(QLabel("Measurements/s: "))
        self.pot_measurement_s_input = QLineEdit()
        pot_row.addWidget(self.pot_measurement_s_input)
        self.pot_widget.setLayout(pot_row)
        pot_row.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.pot_widget)
        self.pot_widget.setVisible(False)

        # Start buttons
        self.start_measurement_btn = QPushButton("Start Measurement")
        layout.addWidget(self.start_measurement_btn)

        #Signals
        self.type_combo.currentIndexChanged.connect(self.update_pot_visibility)

    def update_pot_visibility(self):
        selected = self.type_combo.currentText()
        self.pot_widget.setVisible(selected == "Period of time")

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
        self.output_btn = QPushButton("Output: OFF")

        button_row.addWidget(self.set_configuration_btn)
        button_row.addWidget(self.output_btn)
        layout.addLayout(button_row)

