"""
Sensor Core Coordinator
Runs background telemetry acquisition thread, feeds DSP engine, and distributes real-time frames.
"""

import threading
import time
import asyncio
from typing import List, Dict, Any, Callable
from backend.win32_wifi import Win32WifiMonitor
from backend.dsp_engine import WifiDspEngine

class SensorCore:
    def __init__(self, target_fps: float = 20.0):
        self.target_fps = target_fps
        self.interval = 1.0 / target_fps
        self.monitor = Win32WifiMonitor()
        self.dsp = WifiDspEngine(buffer_size=128, sampling_rate=target_fps)
        
        self.running = False
        self.thread: threading.Thread = None
        self.lock = threading.Lock()
        
        # Latest aggregated frame
        self.latest_frame: Dict[str, Any] = {}
        
        # Subscribers for WebSocket streaming (async queues)
        self.subscribers: List[asyncio.Queue] = []
        self._loop: asyncio.AbstractEventLoop = None

        # Automatically start calibration on launch
        self.dsp.start_calibration(duration_seconds=4.0)

    def set_event_loop(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop

    def add_subscriber(self, q: asyncio.Queue):
        with self.lock:
            self.subscribers.append(q)

    def remove_subscriber(self, q: asyncio.Queue):
        with self.lock:
            if q in self.subscribers:
                self.subscribers.remove(q)

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
        self.monitor.close()

    def trigger_calibration(self, duration_sec: float = 5.0):
        self.dsp.start_calibration(duration_sec)

    def update_config(self, sensitivity: float = None, wall_absorption: float = None):
        if sensitivity is not None:
            self.dsp.sensitivity = max(0.1, min(5.0, float(sensitivity)))
        if wall_absorption is not None:
            self.dsp.wall_absorption = max(0.5, min(3.0, float(wall_absorption)))

    def _worker_loop(self):
        while self.running:
            t_start = time.perf_counter()
            try:
                # 1. Query physical layer metrics
                metrics = self.monitor.query_metrics()
                
                # 2. Process in DSP
                dsp_output = self.dsp.process_sample(metrics)

                # 3. Combine into complete radar telemetry frame
                frame = {
                    "time": round(metrics["timestamp"], 3),
                    "connected": metrics["connected"],
                    "interface": metrics["interface"],
                    "ssid": metrics["ssid"],
                    "bssid": metrics["bssid"],
                    "channel": metrics["channel"],
                    "freq_mhz": metrics["frequency_mhz"],
                    "link_quality": metrics["link_quality"],
                    "tx_rate": metrics["tx_rate_mbps"],
                    "rx_rate": metrics["rx_rate_mbps"],
                    "rssi": metrics["rssi"],
                    "rtt_ms": metrics["rtt_ms"],
                    "gateway": metrics["gateway_ip"],
                    "dsp": dsp_output
                }

                with self.lock:
                    self.latest_frame = frame

                # 4. Broadcast to connected WebSocket queues
                if self._loop and self.subscribers:
                    for q in list(self.subscribers):
                        try:
                            self._loop.call_soon_threadsafe(
                                self._push_to_queue, q, frame
                            )
                        except Exception:
                            pass

            except Exception as e:
                # Keep thread alive on intermittent Windows NDIS query glitched frames
                pass

            elapsed = time.perf_counter() - t_start
            sleep_time = max(0.005, self.interval - elapsed)
            time.sleep(sleep_time)

    def _push_to_queue(self, q: asyncio.Queue, frame: dict):
        try:
            if q.full():
                try:
                    q.get_nowait()
                except Exception:
                    pass
            q.put_nowait(frame)
        except Exception:
            pass
