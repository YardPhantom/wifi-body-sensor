# RF Frequency Allocations, CB Channels, GMRS & Amateur Radio Band Plans

## 1. Exact FCC 40-Channel Citizens Band (CB - 11 Meter) Lookup Table

> [!WARNING]
> **Critical Engineering Note:** CB channel frequencies are **NOT** strictly sequential by 10 kHz!
> - Five 10 kHz slots (`26.995`, `27.045`, `27.095`, `27.145`, `27.195 MHz`) are skipped for Radio Control (R/C) channels (often called "A-channels": 3A, 7A, 11A, 15A, 19A).
> - **Channel 23 (`27.255 MHz`) is higher in frequency than Channel 24 (`27.235 MHz`) and Channel 25 (`27.245 MHz`)** due to historical 23-channel crystal synthesizer allocations.

| Channel | Frequency (MHz) | Standard Mode | Primary Trucker / Citizen Usage |
| :--- | :--- | :--- | :--- |
| **1** | `26.965` | AM | General / East Coast Truckers |
| **2** | `26.975` | AM | General |
| **3** | `26.985` | AM | General / Prepper |
| *(3A)* | *(26.995)* | *R/C / Freeband* | *Skipped in standard 40-ch dial* |
| **4** | `27.005` | AM | Off-Road / 4x4 Trail Channel ("4x4 = Ch 4") |
| **5** | `27.015` | AM | General |
| **6** | `27.025` | AM | **"The Super Bowl"** (High-power linear amp shootout channel) |
| **7** | `27.035` | AM | General |
| *(7A)* | *(27.045)* | *R/C / Freeband* | *Skipped in standard 40-ch dial* |
| **8** | `27.055` | AM | General |
| **9** | `27.065` | AM | **Official Emergency & Traveler Assistance Channel** (FCC Rule) |
| **10** | `27.075` | AM | Secondary Regional Highway / Local Scale Houses |
| **11** | `27.085` | AM | Historical Calling Channel |
| *(11A)* | *(27.095)* | *R/C / Freeband* | *Skipped in standard 40-ch dial* |
| **12** | `27.105` | AM | General |
| **13** | `27.115` | AM | RV / Campers & Marine Pleasure Craft |
| **14** | `27.125` | AM | Walkie-Talkies / Local Yard Operations |
| **15** | `27.135` | AM | West Coast / I-5 Corridor Secondary Trucker Channel |
| *(15A)* | *(27.145)* | *R/C / Freeband* | *Skipped in standard 40-ch dial* |
| **16** | `27.155` | AM / LSB | Historical SSB Calling / ATV Off-Road |
| **17** | `27.165` | AM | North/South Interstate Truckers (I-5 / I-95 overflow) |
| **18** | `27.175` | AM | General |
| **19** | `27.185` | AM | **Primary North American Highway Trucker Channel ("Breaker 1-9")** |
| *(19A)* | *(27.195)* | *R/C / Freeband* | *Skipped in standard 40-ch dial* |
| **20** | `27.205` | AM | General |
| **21** | `27.215` | AM | General |
| **22** | `27.225` | AM | General |
| **23** | `27.255` | AM | *(Note jump to .255!)* General |
| **24** | `27.235` | AM | *(Note step down to .235!)* General |
| **25** | `27.245` | AM | General |
| **26** | `27.265` | AM | DX / AM Skip Calling |
| **27** | `27.275` | AM | General |
| **28** | `27.285` | AM | Big Radio AM Skip / High-Level DX |
| **29** | `27.295` | AM | General |
| **30** | `27.305` | AM | General |
| **31** | `27.315` | AM / FM | Popular FM CB Calling Channel (Post-2021 FCC FM approval) |
| **32** | `27.325` | AM | General |
| **33** | `27.335` | AM / FM | FM CB Operation |
| **34** | `27.345` | AM / SSB | General |
| **35** | `27.355` | AM / SSB | SSB Overflow |
| **36** | `27.365` | LSB / USB | SSB Data / JS8 / Prepper |
| **37** | `27.375` | LSB | SSB DX / Ragchew |
| **38** | `27.385` | **LSB** | **Primary North American SSB Calling & DX Skip Channel (38 LSB)** |
| **39** | `27.395` | LSB / USB | SSB QSO Move-Off Channel |
| **40** | `27.405` | LSB / USB | SSB DX / Regional Net Channel |

* International Freeband DX Calling: **`27.555 MHz` USB** (Listen-only on standard US Part 95 equipment).

---

## 2. NOAA Weather Radio (All Hazards) — 7 Channels (NFM, 25 kHz)

| WX Ch | Frequency (MHz) | S.A.M.E. Alert Tone |
| :--- | :--- | :--- |
| **WX1** | `162.550` | 1050 Hz Warning Tone + AFSK 520.83 baud |
| **WX2** | `162.400` | 1050 Hz Warning Tone + AFSK 520.83 baud |
| **WX3** | `162.475` | 1050 Hz Warning Tone + AFSK 520.83 baud |
| **WX4** | `162.425` | 1050 Hz Warning Tone + AFSK 520.83 baud |
| **WX5** | `162.450` | 1050 Hz Warning Tone + AFSK 520.83 baud |
| **WX6** | `162.500` | 1050 Hz Warning Tone + AFSK 520.83 baud |
| **WX7** | `162.525` | 1050 Hz Warning Tone + AFSK 520.83 baud |

---

## 3. FRS / GMRS 22-Channel Lineup (UHF NFM)

- **Channels 1–7:** `462.5625`, `462.5875`, `462.6125`, `462.6375`, `462.6625`, `462.6875`, `462.7125 MHz` (25 kHz GMRS / 12.5 kHz FRS, up to 5W GMRS).
- **Channels 8–14:** `467.5625` to `467.7125 MHz` (25 kHz steps, 0.5W interstitial 12.5 kHz NFM).
- **Channels 15–22:** `462.5500`, `462.5750`, `462.6000`, `462.6250`, `462.6500`, `462.6750`, `462.7000`, `462.7250 MHz` (Up to 50W GMRS mobile; **Ch 19 (`462.6500 MHz`)** is the GMRS Highway/Overland channel; **Ch 20 (`462.6750 MHz`, 141.3 Hz PL)** is the GMRS Travel/Emergency tone).

---

## 4. Amateur Radio (Ham) Core Bands & Calling Frequencies (ITU Region 2 / US)

| Band | Frequency Range | Default SSB Mode | Key Calling / Digital Frequencies |
| :--- | :--- | :--- | :--- |
| **160m** | `1.800 – 2.000 MHz` | LSB | `1.840` (FT8), `1.900` (LSB Ragchew) |
| **80m / 75m** | `3.500 – 4.000 MHz` | LSB | `3.573` (FT8), `3.842` (JS8), `3.860` (SSTV) |
| **60m** | `5.3305 – 5.4035 MHz` | **USB** *(FCC Rule)* | 5 Channelized allocations (`5330.5`, `5346.5`, `5357.0`, `5371.5`, `5403.5 kHz`) |
| **40m** | `7.000 – 7.300 MHz` | LSB | `7.074` (FT8), `7.078` (JS8), `7.171` (SSTV), `7.200` (LSB Calling) |
| **30m** | `10.100 – 10.150 MHz` | USB (Data/CW only) | `10.136` (FT8), `10.130` (JS8) |
| **20m** | `14.000 – 14.350 MHz` | **USB** | `14.074` (FT8), `14.078` (JS8), `14.230` (SSTV), `14.300` (Maritime/Emergency) |
| **17m** | `18.068 – 18.168 MHz` | USB | `18.100` (FT8) |
| **15m** | `21.000 – 21.450 MHz` | USB | `21.074` (FT8), `21.340` (SSTV) |
| **12m** | `24.890 – 24.990 MHz` | USB | `24.915` (FT8) |
| **10m** | `28.000 – 29.700 MHz` | USB / FM | `28.074` (FT8), `28.400` (USB Calling), `29.000` (AM), `29.600` (FM Simplex) |
| **6m** | `50.000 – 54.000 MHz` | USB / FM | `50.125` (USB Calling), `50.313` (FT8), `52.525` (FM Simplex) |
| **2m** | `144.000 – 148.000 MHz` | FM / USB | **`146.520` (National FM Simplex Calling)**, `144.200` (USB), `144.390` (North America APRS) |
| **1.25m** | `222.000 – 225.000 MHz` | FM | `223.500` (FM Simplex) |
| **70cm** | `420.000 – 450.000 MHz` | FM / USB | **`446.000` (National FM Simplex Calling)**, `432.100` (USB/Weak Signal) |

* **Standard SSB Convention:** Use **LSB** below `10 MHz` (160m, 80m, 40m — *except 60m which is strictly USB* and *CB Ch 38 which is LSB*) and **USB** above `10 MHz` (20m, 17m, 15m, 12m, 10m, 6m, 2m) and for **all digital modes (FT8, JS8, SSTV, RTTY)**.

---

## 5. Standard EIA/TIA 50-Tone CTCSS (PL) Frequency Table (Hz)

```text
67.0, 69.3, 71.9, 74.4, 77.0, 79.7, 82.5, 85.4, 88.5, 91.5,
94.8, 97.4, 100.0, 103.5, 107.2, 110.9, 114.8, 118.8, 123.0, 127.3,
131.8, 136.5, 141.3, 146.2, 151.4, 156.7, 159.8, 162.2, 165.5, 167.9,
171.3, 173.8, 177.3, 179.9, 183.5, 186.2, 189.9, 192.8, 196.6, 199.5,
203.5, 206.5, 210.7, 218.1, 225.7, 229.1, 233.6, 241.8, 250.3, 254.1
```
