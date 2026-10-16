/**
 * Live Doppler & Frequency Spectrogram (Waterfall Chart)
 * Displays time-frequency evolution of microwave perturbation energy.
 */

class WifiSpectrogram {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');
    
    this.maxColumns = 140;
    this.waterfall = []; // Array of columns [ [32 bin values], ... ]
    this.nBins = 32;

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

  pushSpectrum(bins) {
    if (!bins || bins.length === 0) return;
    this.waterfall.push([...bins]);
    if (this.waterfall.length > this.maxColumns) {
      this.waterfall.shift();
    }
  }

  animate() {
    this.draw();
    requestAnimationFrame(() => this.animate());
  }

  draw() {
    const { ctx, width, height, waterfall, nBins } = this;
    ctx.clearRect(0, 0, width, height);

    if (waterfall.length === 0) {
      ctx.fillStyle = 'rgba(74, 99, 130, 0.5)';
      ctx.font = '11px monospace';
      ctx.fillText('Awaiting FFT spectral frames...', 16, height / 2);
      return;
    }

    const colWidth = width / this.maxColumns;
    const rowHeight = height / nBins;

    // Render waterfall pixel matrix
    for (let c = 0; c < waterfall.length; c++) {
      const col = waterfall[c];
      const x = c * colWidth;

      for (let b = 0; b < nBins; b++) {
        // Lower frequencies at bottom, higher at top
        const y = height - (b + 1) * rowHeight;
        const val = Math.min(1.0, Math.max(0.0, col[b]));

        ctx.fillStyle = this.getColormapColor(val);
        ctx.fillRect(x, y, Math.ceil(colWidth), Math.ceil(rowHeight));
      }
    }

    // Overlay frequency region guides
    // Bins 1-3 (~0.15 - 0.45 Hz): Respiration
    // Bins 4-15 (~0.50 - 3.00 Hz): Motion
    const vitalBottomY = height;
    const vitalTopY = height - (3 * rowHeight);
    const motionTopY = height - (15 * rowHeight);

    // Respiration zone label
    ctx.strokeStyle = 'rgba(0, 255, 136, 0.4)';
    ctx.setLineDash([3, 3]);
    ctx.beginPath();
    ctx.moveTo(0, vitalTopY);
    ctx.lineTo(width, vitalTopY);
    ctx.stroke();

    ctx.strokeStyle = 'rgba(255, 170, 0, 0.4)';
    ctx.beginPath();
    ctx.moveTo(0, motionTopY);
    ctx.lineTo(width, motionTopY);
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.font = '9px monospace';
    ctx.fillStyle = '#00ff88';
    ctx.fillText('RESPIRATION BAND (0.15 - 0.45 Hz)', 10, vitalTopY + 12);

    ctx.fillStyle = '#ffaa00';
    ctx.fillText('MACRO MOTION BAND (0.5 - 3.0 Hz)', 10, motionTopY + 12);
  }

  getColormapColor(val) {
    // Thermal gradient: Black -> Navy -> Teal -> Green -> Yellow -> Red
    if (val < 0.05) return '#050811';
    if (val < 0.25) {
      const t = (val - 0.05) / 0.20;
      return `rgb(0, ${Math.floor(t * 120)}, ${Math.floor(100 + t * 155)})`;
    }
    if (val < 0.55) {
      const t = (val - 0.25) / 0.30;
      return `rgb(0, ${Math.floor(120 + t * 135)}, ${Math.floor(255 - t * 180)})`;
    }
    if (val < 0.80) {
      const t = (val - 0.55) / 0.25;
      return `rgb(${Math.floor(t * 255)}, 255, 0)`;
    }
    const t = (val - 0.80) / 0.20;
    return `rgb(255, ${Math.floor(255 - t * 200)}, 20)`;
  }
}

window.WifiSpectrogram = WifiSpectrogram;
