---
name: rf-dsp-sdr-engineering
description: >-
  Principal RF Systems, Digital Signal Processing (DSP), Citizens Band (CB 27 MHz),
  and Software Defined Radio (SDR) engineering skill. Activate this skill whenever
  designing, implementing, debugging, or explaining RF demodulation (AM, NFM, WFM,
  USB, LSB, CW), IQ signal processing, FFT spectrum/waterfall analyzers, CB radio
  channels and audio chains (squelch, ANL, compressor, Roger beep), CTCSS/DCS tones,
  RTL-SDR/HackRF/KiwiSDR integration, or audio/RF filter design.
---

# RF Systems, DSP & SDR Engineering Skill

Apply principal-level RF and Digital Signal Processing (DSP) engineering rigor whenever building or modifying radio, audio, spectrum, or SDR components.

## 1. Core Quadrature (IQ) & Spectral DSP Architecture

1. **Complex Baseband Representation:**
   - Represent RF/IF signals as complex analytic samples $x[n] = I[n] + jQ[n]$.
   - Always remove DC offset spikes at $0\text{ Hz}$ (center LO leakage) using a single-pole high-pass IIR filter before demodulation:
     $$y[n] = x[n] - x[n-1] + \alpha y[n-1], \quad \alpha \in [0.995, 0.999]$$
   - Correct IQ imbalance (gain & phase orthogonality errors) when interfacing with low-cost direct-conversion tuners.

2. **Frequency Translation & Decimation:**
   - Shift off-center channels within captured IQ bandwidth to baseband using a Numerically Controlled Oscillator (NCO):
     $$x_{\text{shifted}}[n] = x[n] \cdot e^{-j 2\pi (f_{\text{offset}} / f_s) n}$$
   - Maintain phase continuity (`phase_acc = (phase_acc + phase_inc) % TAU`) across buffer boundaries to prevent phase-discontinuity clicks.
   - Use multi-stage decimation (CIC or half-band FIR followed by a sharp Windowed-Sinc Blackman-Harris FIR filter) before running audio-rate demodulators. Never downsample without anti-aliasing filtration.

3. **Spectrum & Waterfall FFT Pipeline:**
   - Apply a **4-term Blackman-Harris** or **Hann** window before computing the FFT to suppress spectral leakage (sidelobes $<-92\text{ dB}$ for Blackman-Harris).
   - Convert complex FFT bins $X[k]$ to logarithmic power spectral density (dBFS):
     $$P_{\text{dBFS}}[k] = 10 \log_{10}\left(\frac{\text{Re}(X[k])^2 + \text{Im}(X[k])^2}{N^2} + \epsilon\right), \quad \epsilon = 10^{-12}$$
   - Apply temporal smoothing using an asymmetric Exponential Moving Average (EMA): fast attack ($\alpha_{\text{attack}} \approx 0.6$) to catch transient voice peaks/key-ups, slow decay ($\alpha_{\text{decay}} \approx 0.15$) for readable visual persistence.

---

## 2. Precision Demodulator Implementations

For exact equations and filter topologies, consult [dsp_demodulation_math.md](./references/dsp_demodulation_math.md).

- **AM (Amplitude Modulation — CB Channels 1–40 & Airband):**
  - Bandwidth: $6\text{ kHz}$–$10\text{ kHz}$ IF passband ($\pm 3\text{ to }\pm 5\text{ kHz}$).
  - Envelope detector: $m[n] = \sqrt{I[n]^2 + Q[n]^2}$ (or PLL synchronous detector for deep-fade skywave skip).
  - Follow envelope detection with a DC-blocking high-pass filter ($f_c = 250\text{ Hz}$), an **Automatic Noise Limiter (ANL)** (series envelope slew-rate limiter that clips ignition/static spikes exceeding $1.5\times$ the rolling RMS envelope), and an audio low-pass filter ($f_c = 3200\text{ Hz}$).
- **NFM (Narrowband FM — VHF/UHF Ham 2m/70cm, GMRS/FRS, NOAA Weather, Marine):**
  - Bandwidth: $12.5\text{ kHz}$ ($\pm 2.5\text{ kHz}$ deviation) or $25\text{ kHz}$ ($\pm 5\text{ kHz}$ deviation).
  - Polar conjugate delay discriminator:
    $$\Delta \phi[n] = \text{atan2}\left(\text{Im}(x[n] \cdot x^*[n-1]),\, \text{Re}(x[n] \cdot x^*[n-1])\right)$$
  - Apply a $750\,\mu\text{s}$ (or $75\,\mu\text{s}$) de-emphasis IIR filter after discrimination, and high-pass at $300\text{ Hz}$ to strip sub-audible CTCSS/DCS tones from the speaker path while routing $<300\text{ Hz}$ to the Goertzel CTCSS decoder.
- **SSB (USB / LSB — CB Channels 36–40 Freeband & HF Ham Bands):**
  - Bandwidth: $2.4\text{ kHz}$–$2.8\text{ kHz}$ ($300\text{ Hz}$ to $2700\text{ Hz}$ audio passband).
  - Implement via **Complex Bandpass Filter** on analytic IQ (pass $+300\text{ to }+2700\text{ Hz}$ for USB; $-2700\text{ to }-300\text{ Hz}$ for LSB) and take $\text{Re}(y[n])$, or use the **Weaver / Hilbert Phasing** method.
  - Include a **Fast-Attack, Slow-Decay Hang AGC** (Attack $\approx 2\text{ ms}$, Hang $\approx 300\text{ ms}$, Decay $\approx 500\text{ ms}$) to prevent SSB voice pumping.

---

## 3. Citizens Band (CB 27 MHz) & Trucker Audio Chain Engineering

For the exact 40-channel frequency chart and band plans, consult [frequency_allocations_and_modes.md](./references/frequency_allocations_and_modes.md).

1. **Non-Linear FCC CB Channel Spacing Anomaly:**
   - Do **NOT** calculate CB channel frequencies as a simple linear formula `26.965 + (ch - 1) * 0.010`!
   - The FCC Part 95 CB band skips FIVE 10 kHz R/C channels (`26.995`, `27.045`, `27.095`, `27.145`, `27.195 MHz` — known as 3A, 7A, 11A, 15A, 19A) and **swaps Channels 23, 24, and 25** (`Ch 22 = 27.225 MHz`, `Ch 23 = 27.255 MHz`, `Ch 24 = 27.235 MHz`, `Ch 25 = 27.245 MHz`, `Ch 26 = 27.265 MHz`). Always use the exact lookup table in [frequency_allocations_and_modes.md](./references/frequency_allocations_and_modes.md).
2. **Authentic CB Transmit/Receive Audio DSP Chain:**
   - **Pre-Emphasis & Bandpass:** 4th-order Butterworth bandpass ($300\text{ Hz}$ – $3000\text{ Hz}$) with $+6\text{ dB/octave}$ pre-emphasis boost around $1.8\text{–}2.4\text{ kHz}$ for punchy voice intelligibility over road/engine noise.
   - **Dynamic Speech Compressor ("Dynamike" / Modulation Boost):** Soft-knee compressor (Ratio $4:1$, Threshold $-18\text{ dBFS}$, Attack $5\text{ ms}$, Release $80\text{ ms}$, Makeup Gain $+6\text{ dB}$) followed by a brickwall limiter at $-1.0\text{ dBFS}$ to achieve $95\%\text{–}100\%$ modulation depth without splatter.
   - **Squelch Gate with Hysteresis & Squelch Tail:**
     - Open threshold $\theta_{\text{open}}$ vs. Close threshold $\theta_{\text{close}} = \theta_{\text{open}} - 3\text{ dB}$ to prevent chattering on fluttering mobile signals.
     - On carrier drop (PTT unkey), inject an authentic **$90\text{–}140\text{ ms}$ band-limited pink-noise squelch tail** followed by a soft $10\text{ ms}$ cosine fade-out.
   - **Roger Beep Synthesizer:** Optional end-of-transmission tone burst (Classic Cobra/President single tone: $2475\text{ Hz}$ for $120\text{ ms}$, or NASA/Apollo dual-tone $2525\text{ Hz} \rightarrow 2475\text{ Hz}$).

---

## 4. Hardware SDR & Audio Interface Integration (Windows & Android)

- **RTL-SDR (RTL2832U + R820T2/R828D):**
  - Sample rate: Use $2.048\text{ MS/s}$ or $2.4\text{ MS/s}$ (guaranteed zero-drop rates over USB 2.0). Avoid $>2.56\text{ MS/s}$ where RTL2832U drops samples.
  - For **27 MHz CB (11m)** and **HF (< 28.8 MHz)**: R828D/RTL-SDR Blog V4 has a built-in upconverter/direct-sampling path; older V3 dongles require enabling **Direct Sampling Q-branch mode** (`rtlsdr_set_direct_sampling(dev, 2)`) below $24\text{ MHz}$, while $26.965\text{–}27.405\text{ MHz}$ works directly on the R820T2/R828D PLL tuner!
  - On **Android (Samsung S26 Ultra)**: Access USB OTG via Android `UsbManager` file descriptor (`rtlsdr_open2` or TCP bridge `rtl_tcp` on `127.0.0.1:1234`).
- **Auto-Ducking Mixer:**
  - When mixing Internet Radio / Music streams with active CB or Ham radio voice, trigger an envelope sidechain ducker: attenuate the music stream by $-16\text{ dB}$ to $-20\text{ dB}$ within $15\text{ ms}$ when squelch opens or PTT is pressed, and hold for $600\text{ ms}$ after squelch closes before smoothly restoring volume over $400\text{ ms}$.
