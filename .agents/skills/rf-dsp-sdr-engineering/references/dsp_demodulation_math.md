# Mathematical & Algorithmic Reference for RF Demodulation & Audio DSP

## 1. Windowed-Sinc Complex & Real FIR Filter Synthesis

To construct a low-pass FIR filter of odd length $M$ (order $M-1$) with cutoff frequency $f_c$ at sample rate $f_s$:
- Normalized cutoff: $\Omega_c = 2\pi \frac{f_c}{f_s}$
- Center tap index: $K = \frac{M - 1}{2}$
- Impulse response before windowing:
  $$h_{\text{ideal}}[n] = \begin{cases} \frac{\Omega_c}{\pi}, & n = K \\ \frac{\sin(\Omega_c (n - K))}{\pi (n - K)}, & n \neq K \end{cases}$$
- Multiply by the **4-Term Blackman-Harris Window**:
  $$w[n] = a_0 - a_1 \cos\left(\frac{2\pi n}{M-1}\right) + a_2 \cos\left(\frac{4\pi n}{M-1}\right) - a_3 \cos\left(\frac{6\pi n}{M-1}\right)$$
  where $a_0 = 0.35875$, $a_1 = 0.48829$, $a_2 = 0.14128$, $a_3 = 0.01168$.
- Normalize filter taps for unity passband gain: $h[n] \leftarrow \frac{h_{\text{ideal}}[n] \cdot w[n]}{\sum_k h_{\text{ideal}}[k] \cdot w[k]}$.

### Complex Bandpass Filter (for Single-Step SSB Demodulation)
To pass only upper sideband ($+f_{\text{low}}$ to $+f_{\text{high}}$, e.g. $+300\text{ Hz}$ to $+2700\text{ Hz}$) or lower sideband ($-2700\text{ Hz}$ to $-300\text{ Hz}$):
1. Design a real low-pass prototype $h_{\text{LP}}[n]$ with cutoff $f_c = \frac{f_{\text{high}} - f_{\text{low}}}{2} = 1200\text{ Hz}$.
2. Shift the real prototype to the center of the desired sideband $f_{\text{center}} = \pm \frac{f_{\text{high}} + f_{\text{low}}}{2} = \pm 1500\text{ Hz}$:
   $$h_{\text{complex}}[n] = h_{\text{LP}}[n] \cdot e^{j 2\pi (f_{\text{center}} / f_s)(n - K)}$$
3. Convolve complex baseband input $x[n] = I[n] + jQ[n]$ with $h_{\text{complex}}[n]$ and take the real part $\text{Re}(y[n])$ as the demodulated SSB audio.

---

## 2. S-Meter Calibration Standard (IARU Region 1 / Standard HF & VHF)

- **HF & 11m CB ($< 30\text{ MHz}$):**
  - **S9** $= -73\text{ dBm}$ ($50\,\mu\text{V}$ into $50\,\Omega$).
  - Each **S-unit** below S9 equals **$6\text{ dB}$**:
    $$\text{S-Units} = \text{clamp}\left(9 + \frac{P_{\text{dBm}} - (-73)}{6},\, 0,\, 9\right)$$
  - Above S9, display **$\text{S9} + X\text{ dB}$** ($+10\text{ dB}, +20\text{ dB}, +40\text{ dB}, +60\text{ dB}$).
- **VHF / UHF ($> 30\text{ MHz}$):**
  - **S9** $= -93\text{ dBm}$ ($5\,\mu\text{V}$ into $50\,\Omega$).

---

## 3. Goertzel Algorithm for CTCSS (PL) & DTMF Tone Detection

When detecting discrete tones (such as the 50 CTCSS frequencies or 8 DTMF row/column frequencies) at audio sample rate $f_s$ over block size $N$:
- Precompute target bin & coefficient:
  $$\omega_0 = \frac{2\pi f_{\text{target}}}{f_s}, \quad \text{coeff} = 2\cos(\omega_0)$$
- Per sample $x[n]$ ($n = 0 \dots N-1$):
  $$s_0 = x[n] + \text{coeff} \cdot s_1 - s_2$$
  $$s_2 = s_1, \quad s_1 = s_0$$
- Power at end of block:
  $$P(f_{\text{target}}) = s_1^2 + s_2^2 - \text{coeff} \cdot s_1 \cdot s_2$$
- For CTCSS resolution of $2.3\text{ Hz}$ (separating $67.0\text{ Hz}$ and $69.3\text{ Hz}$), decimate the $<300\text{ Hz}$ sub-audible path to $f_s = 1000\text{ Hz}$ and use block length $N = 500$ ($0.5\text{ s}$ integration window with $50\%$ overlap).

---

## 4. CB Automatic Noise Limiter (ANL) & Noise Blanker (NB)

Ignition noise from diesel trucks, alternators, and powerlines manifests as high-amplitude, short-duration ($<100\,\mu\text{s}$) impulses.
- **IF Noise Blanker (Pre-Filter):**
  - Track running average magnitude $\mu_{\text{mag}}[n] = 0.999 \mu_{\text{mag}}[n-1] + 0.001 |x[n]|$.
  - If $|x[n]| > \eta \cdot \mu_{\text{mag}}[n]$ (typically $\eta \in [4.0, 8.0]$), zero or linear-interpolate complex samples for the next $L$ samples ($\approx 50\,\mu\text{s}$).
- **Audio ANL (Post-Envelope Detector):**
  - Track running audio envelope $E[n]$ via a slow RC filter ($\tau \approx 20\text{ ms}$).
  - Clamp instantaneous audio excursion: $a_{\text{out}}[n] = \text{clamp}(a_{\text{in}}[n], -1.4 E[n], +1.4 E[n])$.
