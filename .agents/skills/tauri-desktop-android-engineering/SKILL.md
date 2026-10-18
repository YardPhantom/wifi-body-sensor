---
name: tauri-desktop-android-engineering
description: Principal Tauri v2 desktop (Windows) and mobile (Android / Samsung Galaxy S26 Ultra) cross-platform architecture, IPC commands, serial/USB hardware bridges, security, and native DSP integrations for HeshRadio.
---

# Principal Tauri v2 Engineering Standards (Desktop & Android)

You are operating as a **Principal Desktop & Mobile Systems Engineer** building **HeshRadio** on the **Tauri v2** framework (`tauri@2.x`, `tauri-build@2.x`, targeting Windows Desktop x86_64/ARM64 and Android aarch64 on Samsung Galaxy S26 Ultra).

## 1. Tauri v2 Core Architecture & Multi-Platform Support

1. **Tauri v2 Configuration (`tauri.conf.json`):**
   - Use `$schema: "https://schema.tauri.app/config/2"`.
   - Never use Tauri v1 syntax (e.g. `tauri > allowlist`). In Tauri v2, permissions are handled by granular capability files in `src-tauri/capabilities/` and plugin crates.
   - For mobile (Android), ensure `frontendDist` points to `"../dist"` and `bundle > targets` is set properly.

2. **Cross-Platform Compilation Targets:**
   - **Windows Desktop:** `x86_64-pc-windows-msvc` (using WebView2 runtime).
   - **Android Mobile:** `aarch64-linux-android` (specifically tested and tuned for high-refresh 120Hz dynamic AMOLED on Samsung Galaxy S26 Ultra).
   - Provide zero-cost compile-time branch abstractions using `#[cfg(target_os = "android")]` and `#[cfg(target_os = "windows")]`.

---

## 2. Low-Latency Rust IPC & State Management

1. **Non-Blocking Commands:**
   - Any IPC command called from the React frontend via `@tauri-apps/api/core` (`invoke`) that performs I/O (file access, network requests, serial port polling, or SDR buffer streaming) MUST be asynchronous:
     ```rust
     #[tauri::command]
     pub async fn tune_frequency(freq_hz: u64, state: State<'_, Mutex<RadioRigState>>) -> Result<RadioRigState, String> {
         let mut lock = state.lock().map_err(|e| e.to_string())?;
         lock.frequency_hz = freq_hz;
         Ok(lock.clone())
     }
     ```
2. **Lock Contention Prevention:**
   - Keep Mutex locks short-lived. Never hold Mutex locks across asynchronous `.await` points or during long-running DSP operations.
   - Use atomic variables (`AtomicBool`, `AtomicU64`) for high-rate telemetry polling (e.g., S-meter signal levels, audio volume decibels, PTT state watchdog).

3. **High-Frequency Telemetry Streaming via Tauri Events:**
   - Do NOT poll IPC commands from the frontend for 60Hz/120Hz waterfall FFT bins or audio levels.
   - Use `app_handle.emit("sdr:fft-data", buffer)` or channel-based events (`tauri::ipc::Channel`) for continuous streaming of raw binary IQ or audio data.

---

## 3. Hardware Integration (USB SDR & CAT Serial Control)

1. **Serial & Rig Control (Digirig, Hamlib, Icom CI-V, Kenwood, Yaesu):**
   - Serial hardware access via `serialport` crate or WebSerial plugin.
   - Baud rate selection: Default to `9600` or `115200` baud, 8 data bits, 1 stop bit, no parity (8N1).
   - DTR / RTS hardware lines must be cleanly toggled for hardware PTT:
     - `port.write_request_to_send(true)` for PTT key.
     - `port.write_request_to_send(false)` for PTT release.
2. **USB RTL-SDR & HackRF Integration:**
   - Desktop: Access via native Rust `librtlsdr` bindings or fallback to WebUSB / `rtl_tcp` network streaming (`localhost:1234`).
   - Android (Samsung S26 Ultra): USB OTG device permission must be handled via Android intent with standard vendor IDs (`0x0bda:0x2838`, `0x0bda:0x2832`).

---

## 4. Fail-Safe PTT & Window Lifecycle Watchdogs

1. **Watchdog Panic-Unkey on Focus Loss:**
   - On Windows or Android, if the user switches apps, minimizes the window, or locks the device, the Tauri backend must automatically trigger fail-safe transmitter unkey.
   - Listen to `tauri::WindowEvent::Focused(false)` or `tauri::WindowEvent::Destroyed` to clear PTT instantly.
2. **Hardware Time-Out-Timer (TOT):**
   - Enforce maximum continuous transmit duration (default: 180 seconds) in the Rust backend. If the frontend hangs or fails to send an unkey event, the backend hardware watchdog must disengage transmission autonomously.

---

## 5. Build, Packaging & Deployment

1. **Windows Build Commands:**
   - Development: `npm run tauri dev` or `cargo tauri dev`.
   - Production Installer: `npm run tauri build` (produces `.msi` and `.exe` NSIS installer in `src-tauri/target/release/bundle/`).
2. **Android Build Commands:**
   - `cargo tauri android init`
   - Development: `cargo tauri android dev`
   - APK/AAB Release: `cargo tauri android build --apk`
