/**
 * High-Frame-Rate RF Multipath Oscilloscope
 * Plots detrended RSSI microwave perturbation alongside microsecond RTT jitter.
 */

class WifiOscilloscope {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');
    
    this.historyLength = 120;
    this.rssiHistory = new Array(this.historyLength).fill(0);
    this.rttHistory = new Array(this.historyLength).fill(0);

    this.resize();
    window.addEventListener('resize', () => this.resize());
    this.animate();
  }

  resize() {
    const rect = this.canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = rect.width * dpr;
    this.canvas.height = rect.height * dpr;
    this.ctx.scale(dpr, dpr);
    this.width = rect.width;
    this.height = rect.height;
  }

  pushSample(filteredMotion, filteredVital) {
    this.rssiHistory.push(filteredMotion);
    if (this.rssiHistory.length > this.historyLength) {
      this.rssiHistory.shift();
    }

    this.rttHistory.push(filteredVital);
    if (this.rttHistory.length > this.historyLength) {
      this.rttHistory.shift();
    }
  }

  animate() {
    this.draw();
    requestAnimationFrame(() => this.animate());
  }

  draw() {
    const { ctx, width, height } = this;
    ctx.clearRect(0, 0, width, height);

    // 1. Grid
    ctx.strokeStyle = 'rgba(26, 42, 68, 0.4)';
    ctx.lineWidth = 1;
    const gridCols = 8;
    const gridRows = 4;

    for (let i = 0; i <= gridCols; i++) {
      const x = (width / gridCols) * i;
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }

    for (let j = 0; j <= gridRows; j++) {
      const y = (height / gridRows) * j;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    // Center Zero Line
    const midY = height / 2;
    ctx.strokeStyle = 'rgba(0, 243, 255, 0.2)';
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(0, midY);
    ctx.lineTo(width, midY);
    ctx.stroke();
    ctx.setLineDash([]);

    // 2. Trace 1: Detrended Carrier Perturbation (Cyan)
    this.renderTrace(this.rssiHistory, '#00f3ff', midY, height * 0.35, 1.5);

    // 3. Trace 2: Microsecond RTT Jitter (Amber)
    this.renderTrace(this.rttHistory, '#ffaa00', midY, height * 0.22, 1.2);

    // 4. Legend Labels
    ctx.font = '10px monospace';
    ctx.fillStyle = '#00f3ff';
    ctx.fillText('● RF CARRIER PERTURBATION (dRSSI)', 14, 18);

    ctx.fillStyle = '#ffaa00';
    ctx.fillText('● MAC DISPERSION JITTER (dRTT)', 230, 18);
  }

  renderTrace(data, color, centerY, scale, lineWidth) {
    if (data.length < 2) return;
    const { ctx, width } = this;
    const stepX = width / (this.historyLength - 1);

    ctx.save();
    ctx.strokeStyle = color;
    ctx.shadowColor = color;
    ctx.shadowBlur = 8;
    ctx.lineWidth = lineWidth;
    ctx.beginPath();

    for (let i = 0; i < data.length; i++) {
      const x = i * stepX;
      // Clamp values to prevent screen clip
      const val = Math.max(-2.5, Math.min(2.5, data[i]));
      const y = centerY - (val * scale);

      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    }
    ctx.stroke();
    ctx.restore();
  }
}

window.WifiOscilloscope = WifiOscilloscope;
