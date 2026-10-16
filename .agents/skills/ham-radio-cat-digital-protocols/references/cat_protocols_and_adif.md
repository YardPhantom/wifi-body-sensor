# CAT Rig Control Protocols, APRS Passcode & ADIF 3.1.4 Reference

## 1. Transceiver CAT Wire Protocols

### A. Kenwood / Elecraft / Xiegu / Modern Yaesu ASCII Protocol
Commands are ASCII strings terminated by `;` (`0x3B`), typically at `38400` or `115200` baud, `8N1`.
- **Read/Set VFO-A Frequency (`FA`):**
  - Query: `FA;`
  - Response / Set (11-digit Hz on Kenwood/Elecraft, 9-digit Hz on Yaesu FT-991A/DX10):
    - Kenwood (`14.074 MHz`): `FA00014074000;`
    - Yaesu (`27.185 MHz` CB Ch 19): `FA027185000;`
- **Read/Set Operating Mode (`MD`):**
  - Query: `MD;` (or `MD0;` on modern Yaesu)
  - Mode map: `1` = LSB, `2` = USB, `3` = CW, `4` = FM, `5` = AM, `6` = FSK/RTTY, `7` = CW-R, `9` = FSK-R / DATA.
- **PTT Key / Unkey:**
  - Transmit Key: `TX;` or `TX1;`
  - Receive Unkey: `RX;`
- **Read S-Meter (`SM`):**
  - Query: `SM0;` $\rightarrow$ Returns `SM00015;` ($0000\text{–}0030$ scale where $15 = \text{S9}$).

### B. Icom CI-V Binary Bus Protocol
Frame structure: `0xFE 0xFE <ToAddr> <FromAddr> <Cmd> [<SubCmd>] [<Data...>] 0xFD`
- Controller (`<FromAddr>`) is always `0xE0`. Common default `<ToAddr>`: IC-7300 = `0x94`, IC-705 = `0xA4`, IC-9700 = `0xA2`.
- **Read Frequency:** `FE FE 94 E0 03 FD`
- **Set Frequency (`0x05`):** Frequency is encoded as 5 bytes of Little-Endian Packed BCD (10 digits in Hz):
  - Example `27,185,000 Hz` (`00 27 18 50 00`):
    `FE FE 94 E0 05 00 50 18 27 00 FD`
- **PTT Control (`0x1C 0x00`):**
  - Key TX: `FE FE 94 E0 1C 00 01 FD`
  - Unkey RX: `FE FE 94 E0 1C 00 00 FD`

### C. Hamlib `rigctld` Network Socket Protocol (Default TCP `127.0.0.1:4532`)
- `f\n` $\rightarrow$ Get frequency in Hz (e.g. `27185000\n`)
- `F 27185000\n` $\rightarrow$ Set frequency to `27.185 MHz` (`RPRT 0\n`)
- `m\n` $\rightarrow$ Get mode and passband (`AM\n6000\n`)
- `M AM 6000\n` $\rightarrow$ Set mode to AM with 6 kHz filter
- `t\n` / `T 1\n` / `T 0\n` $\rightarrow$ Get/Set PTT (`1` = TX, `0` = RX)
- `l STRENGTH\n` $\rightarrow$ Get calibrated S-meter level in dB relative to S9 (`0` = S9, `-18` = S6, `+20` = S9+20dB)

---

## 2. APRS-IS Passcode Generation Algorithm

Standard 16-bit hash for authenticating a licensed callsign on APRS-IS (`rotate.aprs2.net:14580`):

```python
def generate_aprs_passcode(callsign: str) -> int:
    """Compute the standard 16-bit APRS-IS passcode for a callsign (strip SSID)."""
    base_call = callsign.split("-")[0].strip().upper()
    hash_val = 0x73E2
    for i in range(0, len(base_call), 2):
        hash_val ^= ord(base_call[i]) << 8
        if i + 1 < len(base_call):
            hash_val ^= ord(base_call[i + 1])
    return hash_val & 0x7FFF
```

---

## 3. ADIF 3.1.4 (Amateur Data Interchange Format) Specification

Every log export/import MUST conform to ADIF 3.1.4 tag-length-value format `<FIELD_NAME:LENGTH[:TYPE]>VALUE`:

```adif
ADIF Export from HeshRadio v1.0
<ADIF_VER:5>3.1.4
<PROGRAMID:9>HeshRadio
<PROGRAMVERSION:5>1.0.0
<EOH>

<CALL:5>K1ABC <QSO_DATE:8>20261015 <TIME_ON:6>201530 <BAND:3>11m <FREQ:8>27.18500 <MODE:2>AM <RST_SENT:2>59 <RST_RCVD:2>59 <NAME:4>Buck <GRIDSQUARE:6>CN87uq <COMMENT:26>Ch 19 I-5 Northbound Check <EOR>
```

### Mandatory & Recommended ADIF Fields for HeshRadio:
- `CALL`: Contacted station callsign or CB handle
- `QSO_DATE`: UTC Date `YYYYMMDD`
- `TIME_ON` / `TIME_OFF`: UTC Time `HHMMSS`
- `FREQ`: Frequency in **MHz** (e.g., `27.18500`, `14.07400`, `146.52000`)
- `BAND`: `160m`, `80m`, `60m`, `40m`, `30m`, `20m`, `17m`, `15m`, `12m`, `10m`, `11m`, `6m`, `2m`, `70cm`
- `MODE` / `SUBMODE`: `AM`, `FM`, `SSB` (`SUBMODE: USB` or `LSB`), `CW`, `FT8`, `MFSK` (`SUBMODE: JS8`), `SSTV`, `PKT`
- `RST_SENT` / `RST_RCVD`: `59` (Voice) or `599` (CW) or dB SNR (`-08`, `+04` for FT8/JS8)
- `MY_GRIDSQUARE` / `GRIDSQUARE`: 4, 6, or 8 character Maidenhead locator
