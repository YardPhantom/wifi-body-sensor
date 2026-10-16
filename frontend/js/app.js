/**
 * Main Application Controller
 * Handles WebSocket connection, audio telemetry alerts, gauge rendering, and UI synchronization.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize Visualizers
  const radar = new PolarRadar('radarCanvas');
  const oscilloscope = new WifiOscilloscope('scopeCanvas');
  const spectrogram = new WifiSpectrogram('spectrogramCanvas');

  // DOM Elements
  const statusBadge = document.getElementById('statusBadge');
  const statusText = document.getElementById('statusText');
  const elSsid = document.getElementById('elSsid');
  const elBssid = document.getElementById('elBssid');
  const elRssi = document.getElementById('elRssi');
  const elFreq = document.getElementById('elFreq');
  const elRates = document.getElementById('elRates');
  const elRtt = document.getElementById('elRtt');
  const gaugeNumber = document.getElementById('gaugeNumber');
  const stateLabel = document.getElementById('stateLabel');
  const stateDesc = document.getElementById('stateDesc');
  const calibProgress = document.getElementById('calibProgress');

  const btnCalibrate = document.getElementById('btnCalibrate');
  const btnAudio = document.getElementById('btnAudio');
  const btnDemo = document.getElementById('btnDemo');
  const sliderSensitivity = document.getElementById('sliderSensitivity');
  const valSensitivity = document.getElementById('valSensitivity');
  const sliderWall = document.getElementById('sliderWall');
  const valWall = document.getElementById('valWall');

  // Audio Context for Sonar Pings
  let audioCtx = null;
  let audioEnabled = false;
  let lastAudioAlert = 0;
  let isDemoActive = false;

  function initAudio() {
    if (!audioCtx) {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioCtx.state === 'suspended') {
      audioCtx.resume();
    }
  }

  function playSonarPing(freq = 880, duration = 0.15) {
    if (!audioEnabled || !audioCtx) return;
    const now = Date.now();
    if (now - lastAudioAlert < 600) return; // rate limit pings
    lastAudioAlert = now;

    try {
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(freq * 0.5, audioCtx.currentTime + duration);

      gain.gain.setValueAtTime(0.12, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);

      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(audioCtx.currentTime + duration);
    } catch (e) {}
  }

  // Draw Arc Gauge
  const gaugeCanvas = document.getElementById('gaugeCanvas');
  const gctx = gaugeCanvas.getContext('2d');

  function drawGauge(value) {
    const dpr = window.devicePixelRatio || 1;
    const w = 220;
    const h = 120;
    gaugeCanvas.width = w * dpr;
    gaugeCanvas.height = h * dpr;
    gctx.scale(dpr, dpr);

    gctx.clearRect(0, 0, w, h);
    const cx = w / 2;
    const cy = h - 14;
    const radius = 80;

    // Background track
    gctx.beginPath();
    gctx.arc(cx, cy, radius, Math.PI, Math.PI * 2);
    gctx.strokeStyle = 'rgba(26, 42, 68, 0.6)';
    gctx.lineWidth = 14;
    gctx.stroke();

    // Value Arc
    const pct = Math.max(0, Math.min(100, value)) / 100;
    const endAngle = Math.PI + (Math.PI * pct);

    gctx.beginPath();
    gctx.arc(cx, cy, radius, Math.PI, endAngle);
    
    // Dynamic color gradient based on threat
    let strokeColor = '#00f3ff';
    if (value > 70) strokeColor = '#ff3344';
    else if (value > 35) strokeColor = '#ffaa00';
    else if (value > 15) strokeColor = '#00ff88';

    gctx.strokeStyle = strokeColor;
    gctx.shadowColor = strokeColor;
    gctx.shadowBlur = 12;
    gctx.lineWidth = 14;
    gctx.stroke();
    gctx.shadowBlur = 0;
  }

  // WebSocket Connection
  let socket = null;
  function connectWebSocket() {
    const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${proto}//${window.location.host}/ws/radar`;
    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      statusBadge.className = 'status-badge';
      statusText.innerText = 'ONLINE // LINK ACTIVE';
    };

    socket.onmessage = (event) => {
      try {
        let frame = JSON.parse(event.data);
        if (isDemoActive) {
          frame = injectDemoPerturbation(frame);
        }
        processFrame(frame);
      } catch (err) {
        console.error('Frame parse error', err);
      }
    };

    socket.onclose = () => {
      statusBadge.className = 'status-badge alert';
      statusText.innerText = 'DISCONNECTED // RETRYING';
      setTimeout(connectWebSocket, 1500);
    };

    socket.onerror = () => {
      socket.close();
    };
  }

  // Synthetic disturbance generator for testing
  let demoPhase = 0;
  function injectDemoPerturbation(frame) {
    demoPhase += 0.15;
    const simMotion = Math.sin(demoPhase) * 1.5 + Math.cos(demoPhase * 0.4) * 0.8;
    const simScore = Math.abs(simMotion) * 28.0 + 18.0;

    frame.dsp.disturbance_index = Math.min(95, Math.round(simScore));
    frame.dsp.state = simScore > 40 ? 'MOTION' : 'BREATHING';
    frame.dsp.state_desc = simScore > 40 ? '[DEMO] Simulated through-wall pacing' : '[DEMO] Simulated respiration oscillations';
    frame.dsp.filtered_motion = simMotion;
    frame.dsp.filtered_vital = Math.sin(demoPhase * 0.3) * 0.6;
    frame.dsp.estimated_distance_m = 2.1;
    return frame;
  }

  function processFrame(frame) {
    if (!frame || !frame.dsp) return;
    const dsp = frame.dsp;

    // 1. Update Telemetry Ribbon
    elSsid.innerText = frame.ssid || 'N/A';
    elBssid.innerText = frame.bssid || 'Scanning...';
    elRssi.innerText = `${frame.rssi} dBm`;
    elFreq.innerText = `${frame.freq_mhz || 5240} MHz (Ch ${frame.channel || 48})`;
    elRates.innerText = `↓ ${frame.rx_rate} / ↑ ${frame.tx_rate} Mbps`;
    elRtt.innerText = frame.rtt_ms > 0 ? `${frame.rtt_ms.toFixed(2)} ms` : 'Probing...';

    // 2. Update Gauge and Score
    const disturbance = dsp.disturbance_index || 0;
    gaugeNumber.innerText = disturbance.toFixed(1);
    drawGauge(disturbance);

    // 3. Update Status Badges & State Banners
    stateLabel.innerText = `STATE: ${dsp.state}`;
    stateDesc.innerText = dsp.state_desc;

    if (dsp.state === 'CALIBRATING') {
      statusBadge.className = 'status-badge alert';
      statusText.innerText = `CALIBRATING BASELINE (${Math.round((dsp.calibration_progress || 0) * 100)}%)`;
      stateLabel.style.color = '#ffaa00';
    } else if (dsp.state === 'HIGH_DISTURBANCE' || dsp.state === 'MOTION') {
      statusBadge.className = 'status-badge danger';
      statusText.innerText = 'ALERT // TARGET DETECTED';
      stateLabel.style.color = '#ff3344';
      playSonarPing(dsp.state === 'HIGH_DISTURBANCE' ? 1200 : 880, 0.18);
    } else if (dsp.state === 'BREATHING') {
      statusBadge.className = 'status-badge';
      statusBadge.style.borderColor = '#00ff88';
      statusBadge.style.color = '#00ff88';
      statusText.innerText = 'VITAL DETECTED // RESPIRATION';
      stateLabel.style.color = '#00ff88';
      playSonarPing(440, 0.1);
    } else {
      statusBadge.className = 'status-badge';
      statusText.innerText = 'ONLINE // LINK ACTIVE';
      stateLabel.style.color = '#00f3ff';
    }

    // 4. Update Visualizers
    radar.updateData(frame);
    oscilloscope.pushSample(dsp.filtered_motion, dsp.filtered_vital);
    spectrogram.pushSpectrum(dsp.spectrum_bins);
  }

  // Controls Event Listeners
  btnCalibrate.addEventListener('click', async () => {
    btnCalibrate.classList.add('active');
    try {
      await fetch('/api/calibrate', { method: 'POST' });
    } catch (e) {}
    setTimeout(() => btnCalibrate.classList.remove('active'), 4000);
  });

  btnAudio.addEventListener('click', () => {
    initAudio();
    audioEnabled = !audioEnabled;
    btnAudio.classList.toggle('active', audioEnabled);
    btnAudio.innerText = audioEnabled ? '🔊 AUDIO ALERTS: ON' : '🔈 AUDIO ALERTS: OFF';
    if (audioEnabled) playSonarPing(600, 0.2);
  });

  btnDemo.addEventListener('click', () => {
    isDemoActive = !isDemoActive;
    btnDemo.classList.toggle('active', isDemoActive);
    btnDemo.innerText = isDemoActive ? '🧪 DEMO MODE: ACTIVE' : '🧪 SIMULATE DISTURBANCE';
  });

  sliderSensitivity.addEventListener('input', (e) => {
    const val = parseFloat(e.target.value);
    valSensitivity.innerText = `${val.toFixed(1)}x`;
    fetch('/api/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sensitivity: val })
    });
  });

  sliderWall.addEventListener('input', (e) => {
    const val = parseFloat(e.target.value);
    valWall.innerText = `${val.toFixed(1)}x`;
    fetch('/api/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ wall_absorption: val })
    });
  });

  // Start WebSocket
  connectWebSocket();
});
