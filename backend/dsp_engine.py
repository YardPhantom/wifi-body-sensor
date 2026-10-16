"""
Digital Signal Processing (DSP) Engine for Wi-Fi RF Disturbance Sensing
Extracts human motion, breathing rhythms, spectral Doppler shifts, and presence states.
"""

import numpy as np
from collections import deque
import time

class WifiDspEngine:
    def __init__(self, buffer_size: int = 128, sampling_rate: float = 20.0):
        self.buffer_size = buffer_size
        self.fs = sampling_rate  # target sampling rate in Hz (e.g. 20 Hz)
        
        # Ring buffers
        self.time_buffer = deque(maxlen=buffer_size)
        self.rssi_buffer = deque(maxlen=buffer_size)
        self.rtt_buffer = deque(maxlen=buffer_size)
        self.link_buffer = deque(maxlen=buffer_size)
        
        # Baseline calibration
        self.is_calibrating = False
        self.calibration_samples = []
        self.calibration_target_count = 100  # ~5 seconds at 20 Hz
        
        self.baseline_rssi_mean = -50.0
        self.baseline_rssi_std = 0.6
        self.baseline_rtt_mean = 8.0
        self.baseline_rtt_std = 0.8
        self.is_calibrated = False

        # Sensitivity & wall attenuation factors
        self.sensitivity = 1.0       # 0.2 to 3.0 multiplier
        self.wall_absorption = 1.2   # Drywall attenuation compensation (1.0 - 2.5)
        self.ema_disturbance = 0.0   # Smoothed output

    def start_calibration(self, duration_seconds: float = 5.0):
        """Begin collecting ambient noise baseline."""
        self.calibration_target_count = max(40, int(duration_seconds * self.fs))
        self.calibration_samples = []
        self.is_calibrating = True

    def process_sample(self, sample: dict) -> dict:
        """
        Ingests a raw Wi-Fi sample and computes real-time DSP features:
        - Detrended high-pass filtered signal
        - Respiration band power (0.15 - 0.45 Hz)
        - Human motion band power (0.5 - 3.0 Hz)
        - FFT spectrum bins for live waterfall display
        - Disturbance score (0 - 100)
        - Classification state (QUIET, BREATHING, MOTION, TURBULENT)
        """
        t = sample["timestamp"]
        rssi = float(sample["rssi"])
        rtt = float(sample["rtt_ms"]) if sample["rtt_ms"] > 0 else (self.rtt_buffer[-1] if self.rtt_buffer else 10.0)
        link = float(sample["link_quality"])

        # Handle calibration collection
        if self.is_calibrating:
            self.calibration_samples.append((rssi, rtt))
            if len(self.calibration_samples) >= self.calibration_target_count:
                rssi_vals = [s[0] for s in self.calibration_samples]
                rtt_vals = [s[1] for s in self.calibration_samples]
                self.baseline_rssi_mean = float(np.mean(rssi_vals))
                self.baseline_rssi_std = max(float(np.std(rssi_vals)), 0.3)
                self.baseline_rtt_mean = float(np.mean(rtt_vals))
                self.baseline_rtt_std = max(float(np.std(rtt_vals)), 0.4)
                self.is_calibrating = False
                self.is_calibrated = True

        self.time_buffer.append(t)
        self.rssi_buffer.append(rssi)
        self.rtt_buffer.append(rtt)
        self.link_buffer.append(link)

        # Default fallback frame if buffer not yet primed
        if len(self.rssi_buffer) < 16:
            return {
                "disturbance_index": 0.0,
                "state": "INITIALIZING" if not self.is_calibrating else "CALIBRATING",
                "state_desc": "Buffering initial RF samples...",
                "is_calibrating": self.is_calibrating,
                "is_calibrated": self.is_calibrated,
                "raw_rssi": rssi,
                "raw_rtt": rtt,
                "filtered_motion": 0.0,
                "filtered_vital": 0.0,
                "breathing_bpm": 0,
                "dominant_freq_hz": 0.0,
                "spectrum_bins": [0.0] * 32,
                "estimated_distance_m": 0.0,
                "calibration_progress": len(self.calibration_samples) / max(1, self.calibration_target_count) if self.is_calibrating else 1.0
            }

        # Convert ring buffers to numpy arrays
        rssi_arr = np.array(self.rssi_buffer, dtype=np.float64)
        rtt_arr = np.array(self.rtt_buffer, dtype=np.float64)
        
        # 1. Detrend signal (High-pass / DC removal)
        # Using running mean subtraction over the last window
        window_len = min(len(rssi_arr), 32)
        rssi_detrended = rssi_arr - np.mean(rssi_arr[-window_len:])
        rtt_detrended = rtt_arr - np.mean(rtt_arr[-window_len:])

        # 2. Windowed Variance & Jerk (Rate of Change)
        recent_rssi = rssi_arr[-16:]
        recent_rtt = rtt_arr[-16:]
        rssi_var = float(np.var(recent_rssi))
        rtt_var = float(np.var(recent_rtt))

        # 3. FFT Spectral Decomposition
        n_fft = min(len(rssi_detrended), 64)
        # Combine normalized RSSI and RTT deviations
        norm_combined = (rssi_detrended[-n_fft:] / max(self.baseline_rssi_std, 0.4)) + \
                        (rtt_detrended[-n_fft:] / max(self.baseline_rtt_std, 0.5)) * 0.7
        
        # Apply Hanning window
        window = np.hanning(n_fft)
        fft_vals = np.abs(np.fft.rfft(norm_combined * window))
        freqs = np.fft.rfftfreq(n_fft, d=1.0 / self.fs)

        # 4. Band energy extraction
        # Human Respiration: 0.15 Hz to 0.45 Hz (9 - 27 breaths/min)
        # Human Macro Motion: 0.50 Hz to 3.0 Hz (walking, arm gestures)
        vital_mask = (freqs >= 0.15) & (freqs <= 0.45)
        motion_mask = (freqs >= 0.50) & (freqs <= 3.0)

        vital_energy = float(np.sum(fft_vals[vital_mask])) if np.any(vital_mask) else 0.0
        motion_energy = float(np.sum(fft_vals[motion_mask])) if np.any(motion_mask) else 0.0

        # Peak dominant frequency
        valid_freq_mask = (freqs >= 0.15) & (freqs <= 4.0)
        if np.any(valid_freq_mask) and len(fft_vals[valid_freq_mask]) > 0:
            peak_idx = np.argmax(fft_vals[valid_freq_mask])
            dominant_freq = float(freqs[valid_freq_mask][peak_idx])
        else:
            dominant_freq = 0.0

        # Estimated breathing BPM if in respiration zone
        breathing_bpm = int(round(dominant_freq * 60)) if (0.15 <= dominant_freq <= 0.45) else 0

        # 5. Composite Disturbance Index (0 - 100)
        # Anomaly metric relative to baseline
        z_rssi = max(0.0, (rssi_var / max(self.baseline_rssi_std ** 2, 0.1)) - 1.0)
        z_rtt = max(0.0, (rtt_var / max(self.baseline_rtt_std ** 2, 0.1)) - 1.0)
        
        # Raw disturbance combination
        raw_score = (
            (z_rssi * 18.0) +
            (z_rtt * 15.0) +
            (motion_energy * 4.5) +
            (vital_energy * 2.0)
        ) * self.sensitivity * self.wall_absorption

        # Clamp and exponential smooth
        clamped_score = min(100.0, max(0.0, raw_score))
        self.ema_disturbance = (self.ema_disturbance * 0.75) + (clamped_score * 0.25)
        disturbance_index = round(self.ema_disturbance, 1)

        # 6. State Classification
        if self.is_calibrating:
            state = "CALIBRATING"
            state_desc = f"Learning RF baseline... {int(len(self.calibration_samples)/self.calibration_target_count*100)}%"
        elif disturbance_index < 14.0:
            state = "QUIET"
            state_desc = "Channel clear. No through-wall perturbation."
        elif 14.0 <= disturbance_index < 35.0:
            if breathing_bpm > 0 and vital_energy > (motion_energy * 0.8):
                state = "BREATHING"
                state_desc = f"Subtle presence detected (Breathing rhythm ~{breathing_bpm} BPM)"
            else:
                state = "MICRO_MOTION"
                state_desc = "Minor RF multipath fluctuation detected."
        elif 35.0 <= disturbance_index < 70.0:
            state = "MOTION"
            state_desc = "Human movement active behind wall."
        else:
            state = "HIGH_DISTURBANCE"
            state_desc = "Intense motion / close proximity perturbation."

        # 7. Resample FFT to 32 normalized bins for frontend waterfall
        n_bins = 32
        if len(fft_vals) >= n_bins:
            sub_spectrum = fft_vals[:n_bins]
        else:
            sub_spectrum = np.pad(fft_vals, (0, n_bins - len(fft_vals)), 'constant')
        norm_spectrum = [float(np.clip(v / 25.0, 0.0, 1.0)) for v in sub_spectrum]

        # 8. Estimated Radial Distance (m)
        # Derived from path-loss disturbance inverse attenuation
        if disturbance_index >= 14.0:
            # Stronger disturbance -> closer to wall/radio
            dist = max(0.5, 4.5 - (disturbance_index / 100.0) * 3.5)
        else:
            dist = 0.0

        return {
            "disturbance_index": disturbance_index,
            "state": state,
            "state_desc": state_desc,
            "is_calibrating": self.is_calibrating,
            "is_calibrated": self.is_calibrated,
            "raw_rssi": rssi,
            "raw_rtt": rtt,
            "filtered_motion": round(float(rssi_detrended[-1]), 3),
            "filtered_vital": round(float(rtt_detrended[-1]), 3),
            "breathing_bpm": breathing_bpm,
            "dominant_freq_hz": round(dominant_freq, 2),
            "spectrum_bins": norm_spectrum,
            "estimated_distance_m": round(dist, 2),
            "calibration_progress": len(self.calibration_samples) / max(1, self.calibration_target_count) if self.is_calibrating else 1.0
        }
