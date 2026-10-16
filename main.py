"""
WiFi Body Sensor - Telus Wi-Fi Modem Through-Wall Radar
Launches FastAPI backend server and opens browser HUD.
"""

import os
import sys
import webbrowser
import threading
import time
import uvicorn

def open_browser():
    time.sleep(1.2)
    url = "http://127.0.0.1:8000"
    print(f"\n[+] Opening WiFi Body Sensor Dashboard in your default browser: {url}\n")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Could not open browser automatically: {e}")

def main():
    print("=" * 70)
    print("   WIFI BODY SENSOR // TELUS WI-FI MODEM THROUGH-WALL RADAR")
    print("=" * 70)
    print("[*] Initializing Win32 Native Wifi interface and ICMP prober...")
    print("[*] DSP Engine: Butterworth Filtering + FFT Spectral Decomposition")
    print("[*] Web UI: Polar Radar + Oscilloscope + Doppler Waterfall")
    print("[*] Serving at: http://127.0.0.1:8000")
    print("=" * 70)

    # Launch browser in separate background thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Run uvicorn server
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, log_level="info")

if __name__ == "__main__":
    main()
