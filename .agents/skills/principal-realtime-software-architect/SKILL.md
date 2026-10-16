---
name: principal-realtime-software-architect
description: >-
  Principal Systems & Cross-Platform Software Engineering skill for real-time
  audio, RF/SDR telemetry, low-latency network PTT, and 120Hz tactical UI
  applications across Windows Desktop and Android (Samsung S26 Ultra). Activate
  whenever architecting or writing backend DSP pipelines, lock-free ring buffers,
  WebRTC/WebSocket audio streaming, USB/Serial hardware drivers, or high-FPS
  Canvas/WebGL spectrum and waterfall visualizers.
---

# Principal Real-Time Systems & Cross-Platform Software Architecture Skill

Apply Principal Systems Software Engineer standards across all backend, DSP, networking, and UI code for Windows Desktop and Android (Samsung Galaxy S26 Ultra).

## 1. Real-Time Audio & IQ DSP Threading Invariants

1. **Zero-Allocation Hot-Path Rule:**
   - Inside audio callbacks (WASAPI / AAudio / WebAudio `AudioWorklet`) and SDR USB IQ read threads:
     - **NEVER** allocate heap memory (`malloc`, `Vec::push` without pre-capacity, `new Float32Array` per frame).
     - **NEVER** acquire blocking locks (`Mutex::lock`), perform disk I/O, or make network syscalls.
   - Pre-allocate all FFT scratch buffers, FIR delay lines, and audio frames at initialization time.
2. **Lock-Free SPSC Ring Buffers:**
   - Pass IQ samples and audio PCM chunks between hardware capture threads, DSP worker threads, and UI telemetry pipelines using lock-free Single-Producer Single-Consumer (SPSC) ring buffers with atomic `Acquire`/`Release` memory ordering.
3. **Platform Low-Latency Audio Tuning:**
   - **Windows Desktop:** Prefer WASAPI Shared Low-Latency ($10\text{ ms}$ period) or WASAPI Exclusive mode ($3\text{–}5\text{ ms}$) with Multimedia Class Scheduler Service (`AvSetMmThreadCharacteristicsW(L"Pro Audio")`).
   - **Android (Samsung S26 Ultra):** Use AAudio/Oboe with `AAUDIO_PERFORMANCE_MODE_LOW_LATENCY` and `AAUDIO_SHARING_MODE_SHARED` (or `EXCLUSIVE`), foreground service type `microphone | connectedDevice | mediaPlayback` so PTT and CB monitoring continue uninterrupted when the screen is off or in split-screen navigation.

---

## 2. 60–120Hz GPU/Canvas Spectrum & Waterfall Engineering

1. **Zero-Copy Scrolling Waterfall Buffer:**
   - Never redraw $N \times H$ individual rectangles on a 2D Canvas every frame.
   - Use an offscreen pixel buffer (`Uint32Array` backed by `ImageData` or WebGL2 2D texture with `gl.texSubImage2D` row-ring indexing):
     - Shift existing scanlines down by 1 row (`copyWithin` on `Uint32Array` takes $<0.05\text{ ms}$ for $1024 \times 300$ pixels!) and write only the newly arrived FFT row at index `0` using a precomputed 256-entry RGBA `Uint32Array` Color Look-Up Table (LUT).
2. **Tactical Radio Ergonomics (Desktop + S26 Ultra Touch):**
   - Support mouse wheel tuning over individual frequency digits on Windows AND momentum rotary dial / direct keypad / large thumb PTT bar on the S26 Ultra ($6.9"$ QHD+ Dynamic AMOLED 2X, $120\text{ Hz}$).
   - Provide instantaneous visual and audible feedback for PTT state (`RX` Green / `SQUELCH OPEN` Cyan / `TX ON AIR` High-Contrast Red-Amber glow with SWR & Modulation % meter).

---

## 3. Resilient Networked PTT, WebSDR & Internet Radio Streaming

1. **Adaptive Jitter Buffer & Packet Loss Concealment (PLC):**
   - Frame real-time PTT voice in $20\text{ ms}$ chunks ($48\text{ kHz}$ or $16\text{ kHz}$ mono).
   - Use a dynamic jitter buffer ($40\text{–}120\text{ ms}$) to absorb cellular 5G handoffs on the S26 Ultra without metallic audio artifacts.
2. **Fault-Tolerant Hardware & Stream Lifecycle:**
   - Every hardware adapter (RTL-SDR USB, Serial CAT COM port, Microphone input) and network stream (Icecast Internet Radio, KiwiSDR WebSocket, CB PTT room) must implement:
     - Clean **Graceful Degradation / Simulation Fallback**: If physical SDR or Serial CAT hardware is unplugged, automatically switch to Network WebSDR / Simulated RF Test Signal generator with a clear status badge (`SIM / NET SDR` vs `HW USB SDR`) rather than crashing.
     - Exponential backoff reconnection with jitter ($500\text{ ms} \rightarrow 1\text{ s} \rightarrow 2\text{ s} \rightarrow 5\text{ s}$ cap).

---

## 4. Verification, Telemetry & Engineering Rigor

- **Self-Test & Loopback Diagnostics:**
  - Include built-in synthetic RF/Audio test generators (e.g., Synthetic CB Ch 19 trucker traffic, two-tone SSB IMD test signal at $700\text{ Hz} + 1900\text{ Hz}$, NOAA 1050 Hz alert test, and S9 $-73\text{ dBm}$ calibration tone) so every filter, S-meter, squelch gate, auto-ducker, and waterfall can be deterministically verified without waiting for live over-the-air transmissions.
