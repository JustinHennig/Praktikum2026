# This file contains the SnapshotService, which is responsible for reading waveform data and saving it as a CSV file.
# The data can be put into a graph using the read_from_csv.py file under the folder utils.

import struct
import math
import csv
import datetime
from pathlib import Path

from PySide6.QtCore import QObject, Signal

from app.scpi_commands.sds_commands import (
    get_waveform_data, set_waveform_points, stop_trigger, start_trigger,
    set_waveform_source, set_waveform_start, set_waveform_width,
    get_preamble, get_max_points,
)
from app.scpi_commands.device_independent_commands import open_message_resource


class SnapshotService(QObject):
    finished = Signal(str)       # path to saved CSV
    progress = Signal(int, int)  # (current_chunk, total_chunks)
    error    = Signal(str)

    def __init__(self):
        super().__init__()
        self._cancelled = False

    # Main method to run the process of reading the data, converting it, applying smoothing and saving it to a CSV file.
    def run(self, resource: str, channel: int, points: int, filename: str, smoothing: str):
        try:
            self._cancelled = False
            stop_trigger(resource)

            preamble  = self._read_preamble(resource, channel)
            raw_codes = self._read_raw_data(resource, points, preamble)

            if self._cancelled:
                start_trigger(resource)
                return

            times, voltages = self._convert(raw_codes, preamble)
            voltages = self._apply_smoothing(voltages, smoothing)
            path = self._save_csv(times, voltages, preamble, filename)

            start_trigger(resource)
            self.finished.emit(str(path))
        except Exception as e:
            self.error.emit(str(e))

    # Method to signal cancellation of the data reading process.
    def cancel(self):
        self._cancelled = True

    # Method to read the preamble data from the oscilloscope, which contains important configuration and is used to convert the raw codes into voltage and time.
    def _read_preamble(self, resource: str, channel: int) -> dict:
        set_waveform_source(resource, channel)
        set_waveform_start(resource, 0)
        raw = get_preamble(resource)

        hash_pos = raw.find(b'#')
        desc = raw[hash_pos + 11:]

        comm_order   = struct.unpack_from('<h', desc, 0x22)[0]
        endian       = '>' if comm_order else '<'
        vdiv         = struct.unpack_from(f'{endian}f', desc, 0x9C)[0]
        voffset      = struct.unpack_from(f'{endian}f', desc, 0xA0)[0]
        code_per_div = struct.unpack_from(f'{endian}f', desc, 0xA4)[0]
        adc_bit      = struct.unpack_from(f'{endian}h', desc, 0xAC)[0]
        interval     = struct.unpack_from(f'{endian}f', desc, 0xB0)[0]
        delay        = struct.unpack_from(f'{endian}d', desc, 0xB4)[0]
        probe        = struct.unpack_from(f'{endian}f', desc, 0x148)[0]
        wave_count   = struct.unpack_from(f'{endian}l', desc, 0x74)[0]

        vdiv    *= probe
        voffset *= probe

        return {
            'vdiv': vdiv, 'voffset': voffset, 'code_per_div': code_per_div,
            'adc_bit': adc_bit, 'interval': interval, 'delay': delay,
            'probe': probe, 'wave_count': wave_count, 'endian': endian,
        }

    # This method reads the raw waveform data in chunks, converts it to signed integers, and emits progress signals. It also checks for cancellation between chunks.
    def _read_raw_data(self, resource: str, requested_pts: int, preamble: dict) -> list[int]:
        adc_bit   = preamble['adc_bit']
        endian    = preamble['endian']
        total_pts = min(requested_pts, preamble['wave_count'])

        if adc_bit > 8:
            set_waveform_width(resource, 'WORD')
            bytes_per_sample = 2
        else:
            set_waveform_width(resource, 'BYTE')
            bytes_per_sample = 1

        max_pts     = get_max_points(resource)
        read_chunks = math.ceil(total_pts / max_pts)
        
        raw_codes: list[int] = []

        for chunk_idx in range(read_chunks):
            if self._cancelled:
                break

            start_pt       = chunk_idx * max_pts
            pts_this_chunk = min(max_pts, total_pts - start_pt)

            set_waveform_start(resource, start_pt)
            set_waveform_points(resource, pts_this_chunk)
            chunk_raw = get_waveform_data(resource).rstrip(b'\n')

            hash_pos   = chunk_raw.find(b'#')
            n_digits   = int(chunk_raw[hash_pos + 1 : hash_pos + 2])
            data_start = hash_pos + 2 + n_digits
            payload    = chunk_raw[data_start:]

            if bytes_per_sample == 1:
                for b in payload:
                    raw_codes.append(b if b <= 127 else b - 256)
            else:
                for i in range(0, len(payload) - 1, 2):
                    raw_codes.append(struct.unpack_from(f'{endian}h', payload, i)[0])

            self.progress.emit(chunk_idx + 1, read_chunks)

        return raw_codes

    # Method to convert the raw codes into voltage and time values using the preamble info. 
    def _convert(self, raw_codes: list[int], preamble: dict) -> tuple[list[float], list[float]]:
        vdiv         = preamble['vdiv']
        voffset      = preamble['voffset']
        code_per_div = preamble['code_per_div']
        interval     = preamble['interval']
        delay        = preamble['delay']
        n            = len(raw_codes)

        voltages = [code / code_per_div * vdiv - voffset for code in raw_codes]
        times    = [-delay - (interval * n / 2) + i * interval for i in range(n)]
        return times, voltages

    # This method applies the selected smoothing algorithm to the voltage data. It supports 'None', 'Moving Average', and 'Savitzky-Golay' methods, and automatically determines the window size based on the number of data points.
    def _apply_smoothing(self, voltages: list[float], method: str) -> list[float]:
        if method == 'None' or len(voltages) < 5:
            return voltages

        import numpy as np
        arr    = np.array(voltages)
        window = max(5, len(arr) // 500)

        if method == 'Moving Average':
            kernel = np.ones(window) / window
            return [float(x) for x in np.convolve(arr, kernel, mode='same')]

        if method == 'Savitzky-Golay':
            from scipy.signal import savgol_filter
            if window % 2 == 0:
                window += 1
            return [float(x) for x in savgol_filter(arr, window_length=window, polyorder=3)]

        return voltages

    # Method to convert the voltage and time data into a CSV file and includes the preamble information on top of the file.
    def _save_csv(self, times: list[float], voltages: list[float], preamble: dict, filename: str) -> Path:
        output_dir = Path(__file__).parent.parent.parent / 'data'
        output_dir.mkdir(exist_ok=True)
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        path = output_dir / f'{filename}_{timestamp}.csv'

        # Write CSV file with premable info on top and then the time and voltage data
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([f'# V/div: {preamble["vdiv"]} V'])
            writer.writerow([f'# Offset: {preamble["voffset"]} V'])
            writer.writerow([f'# Abtastintervall: {preamble["interval"]} s'])
            writer.writerow([f'# Trigger-Delay: {preamble["delay"]} s'])
            writer.writerow([f'# Probe: {preamble["probe"]}x'])
            writer.writerow([f'# ADC-Bits: {preamble["adc_bit"]}'])
            writer.writerow([f'# Datenpunkte: {len(voltages)}'])
            writer.writerow(['time_s', 'voltage_V'])
            writer.writerows(zip(times, voltages))

        return path