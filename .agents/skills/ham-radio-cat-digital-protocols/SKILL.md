---
name: ham-radio-cat-digital-protocols
description: >-
  Extra-Class Amateur Radio engineering skill for transceiver CAT rig control
  (Kenwood, Yaesu, Icom CI-V, Hamlib rigctld, Digirig CM108/Serial PTT), digital
  modes (FT8, JS8Call, APRS AX.25/AFSK, SSTV, RTTY, CW), ADIF 3.1.4 logging,
  Maidenhead Grid Square geodesy, and Ionospheric Propagation / Solar Weather physics.
  Activate this skill whenever working on rig control, digital mode modems, APRS
  mapping, QSO logging, callsign lookup, or HF/11m skywave propagation.
---

# Amateur Radio CAT, Digital Modes, Logging & Propagation Engineering Skill

Use this skill to engineer standards-compliant Amateur Radio rig control, digital mode modems, QSO logging, and ionospheric propagation tools.

## 1. Transceiver CAT Control & Hardware PTT Architecture

For wire-level protocol byte framing (Kenwood/Elecraft ASCII, Yaesu CAT, Icom CI-V BCD, and Hamlib `rigctld`), consult [cat_protocols_and_adif.md](./references/cat_protocols_and_adif.md).

1. **Multi-Backend CAT Abstraction Layer:**
   - Implement a unified `RigController` trait/interface supporting:
     - **Hamlib `rigctld` TCP Client** (default `127.0.0.1:4532`) for instant compatibility with 300+ transceivers.
     - **Direct Serial / USB-OTG CAT** (`Kenwood/Elecraft/Xiegu`, `Yaesu FT-891/991A/DX10/818`, `Icom CI-V`) over Windows COM ports and Android `UsbManager` CDC-ACM / FTDI / CP210x / CH340 drivers.
   - Poll VFO frequency (`get_freq`), mode (`get_mode`), and S-meter/SWR (`get_level`) at $5\text{–}10\text{ Hz}$ with non-blocking timeouts ($150\text{ ms}$) and automatic serial port reconnect.
2. **Fail-Safe Hardware PTT (Push-To-Talk) Watchdog:**
   - Support 4 PTT mechanisms:
     1. **CAT Command PTT** (`TX;` / `RX;` or CI-V `0x1C 0x00`).
     2. **Serial Control Line PTT** (`RTS` or `DTR` pin assertion — standard for Digirig Mobile, SignaLink, and opto-isolated cables).
     3. **CM108 / CM119 USB Audio HID GPIO PTT** (Bit 2 / GPIO3 on USB Vendor `0x0D8C`, used by AllStar, Direwolf, and Digirig VOX-less interfaces).
     4. **VOX Pilot Tone** (optional high-level audio routing).
   - **Mandatory Safety Rule — TOT (Time-Out Timer):** Every PTT state machine MUST enforce a hardware/software **Time-Out Timer** (default $180\text{ s}$, configurable $30\text{–}300\text{ s}$) and an immediate **Panic Unkey (`RX`)** on window blur, WebSocket disconnect, or audio callback crash so a transmitter can never get stuck keyed on air.

---

## 2. Digital Modes & Packet Radio Engineering

1. **APRS (Automatic Packet Reporting System — 144.390 MHz NA / 144.800 MHz EU & CB/Tactical IP):**
   - **Physical Layer:** Bell 202 AFSK at $1200\text{ baud}$ ($1200\text{ Hz}$ Mark, $2200\text{ Hz}$ Space, continuous-phase FSK).
   - **Link Layer:** AX.25 UI frames with NRZI encoding (bit transition on `0`, no transition on `1`), bit-stuffing (insert `0` after five consecutive `1`s), `0x7E` HDLC flag bytes, and CRC-16-CCITT (`0x8408` reflected polynomial).
   - **APRS-IS TCP/IP Gateway:** Connect to `rotate.aprs2.net:14580` (or `noam.aprs2.net:14580`). Authenticate with `user <CALLSIGN> pass <PASSCODE> vers HeshRadio 1.0 filter r/<lat>/<lon>/<radius_km>`.
2. **FT8 / JS8 Weak-Signal HF Modes:**
   - **Critical Timing Requirement:** FT8 uses $15.0\text{ s}$ T/R sequences ($12.64\text{ s}$ 8-FSK symbol transmission at $6.25\text{ baud}$, $6.25\text{ Hz}$ tone spacing = $50\text{ Hz}$ total bandwidth). System clock MUST be synchronized within $\pm 0.5\text{ s}$ of UTC via NTP (`pool.ntp.org`) before decoding or transmitting.
   - Always operate transceiver in **USB** (or `USB-DATA` / `PKTUSB`) with all transmit audio EQ, compression, and noise reduction **disabled** (flat passband).
3. **SSTV (Slow Scan Television):**
   - Decode starting on the **VIS header** ($1900\text{ Hz}$ leader $\rightarrow$ $1200\text{ Hz}$ break $\rightarrow$ $1900\text{ Hz}$ leader $\rightarrow$ 8-bit VIS code at $1100\text{ Hz} = 1$, $1300\text{ Hz} = 0$).
   - Map instantaneous frequency between $1500\text{ Hz}$ (Black $= 0$) and $2300\text{ Hz}$ (White $= 255$) across scanlines aligned by $1200\text{ Hz}$ horizontal sync pulses. Support **Martin M1**, **Scottie S1**, and **Robot 36**.

---

## 3. Maidenhead Grid Square Geodesy & Great Circle Math

Always compute exact Maidenhead 6-character locators (e.g., `CN87uq`, `FN31pr`) and Great Circle azimuth/distance:
- **Lat/Lon ($\phi, \lambda$ in degrees) to 6-Char Grid Square:**
  1. Normalize: $\Lambda = \lambda + 180^\circ$, $\Phi = \phi + 90^\circ$.
  2. **Field (Chars 1–2, `A–R`):** $L_1 = \lfloor \Lambda / 20 \rfloor$, $L_2 = \lfloor \Phi / 10 \rfloor$.
  3. **Square (Chars 3–4, `0–9`):** $S_1 = \lfloor (\Lambda \bmod 20) / 2 \rfloor$, $S_2 = \lfloor \Phi \bmod 10 \rfloor$.
  4. **Subsquare (Chars 5–6, `a–x`):** $u_1 = \lfloor ((\Lambda \bmod 2) \times 12) \rfloor$, $u_2 = \lfloor ((\Phi \bmod 1) \times 24) \rfloor$.
- **Great Circle Distance & Short-Path / Long-Path Bearing:**
  - Use the Haversine formula ($R_{\text{earth}} = 6371.0\text{ km}$) for distance $d$, and forward azimuth:
    $$\theta = \text{atan2}\left(\sin(\Delta\lambda)\cos(\phi_2),\, \cos(\phi_1)\sin(\phi_2) - \sin(\phi_1)\cos(\phi_2)\cos(\Delta\lambda)\right)$$
  - Long-path bearing: $\theta_{\text{LP}} = (\theta_{\text{SP}} + 180^\circ) \bmod 360^\circ$; Long-path distance: $40030\text{ km} - d_{\text{SP}}$.

---

## 4. Ionospheric Propagation, 11m/10m Skip & Solar Telemetry

- **Live NOAA SWPC Telemetry Feeds:**
  - Fetch 10.7 cm Solar Flux Index (SFI), Planetary $K_p$ Index, and A-Index from NOAA Space Weather Prediction Center JSON endpoints (`https://services.swpc.noaa.gov/json/`).
- **11-Meter (27 MHz CB) & 10-Meter (28 MHz) "Skip" Prediction:**
  - **F2 Layer Skywave Skip** opens on 27–29 MHz during daytime/greyline when **$\text{SFI} > 110$** and **$K_p \le 3$**, where the Maximum Usable Frequency ($\text{MUF} = f_oF2 \cdot M(3000)F2$) exceeds $27.0\text{ MHz}$ (single-hop skip distance $1200\text{–}3500\text{ km}$).
  - **Sporadic-E ($E_s$)** opens intense short-to-medium skip ($500\text{–}2200\text{ km}$) on 11m CB, 10m, and 6m (`50 MHz`) predominantly during May–August and December regardless of SFI.
- **Solar Greyline (Terminator) Calculation:**
  - Compute solar declination $\delta_\odot$ and Greenwich Hour Angle $\text{GHA}_\odot$ from current UTC time; plot the locus of points where solar zenith angle $Z = 90^\circ$ (with $\pm 5^\circ$ twilight enhancement band where D-layer absorption vanishes while F-layer ionization remains high).
