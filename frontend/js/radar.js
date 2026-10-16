/**
 * Polar Radar and Through-Wall Cross-Section Canvas Visualizer
 */

class PolarRadar {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');
    this.sweepAngle = 0;
    this.sweepSpeed = 0.035; // radians per frame
    
    // Echo targets [ { x, y, radius, alpha, intensity, label } ]
    this.echoes = [];
    this.latestDisturbance = 0.0;
    this.latestDistance = 0.0;
    this.latestState = 'QUIET';

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
    this.cx = this.width / 2;
    this.cy = this.height * 0.85; // Place desktop transceiver near lower center
    this.maxRadius = this.height * 0.72;
  }

  updateData(frame) {
    if (!frame || !frame.dsp) return;
    this.latestDisturbance = frame.dsp.disturbance_index || 0.0;
    this.latestDistance = frame.dsp.estimated_distance_m || 0.0;
    this.latestState = frame.dsp.state || 'QUIET';

    // Spawn echo ripples if motion or respiration detected
    if (this.latestDisturbance > 14.0) {
      const distRatio = Math.max(0.2, Math.min(0.9, (this.latestDistance / 4.5)));
      const distPx = this.maxRadius * distRatio;
      
      // Slight angular dispersion representing multipath scatter
      const jitterAngle = (Math.random() - 0.5) * 0.45;
      const targetAngle = -Math.PI / 2 + jitterAngle; // towards top (facing AP)

      this.echoes.push({
        x: this.cx + Math.cos(targetAngle) * distPx,
        y: this.cy + Math.sin(targetAngle) * distPx,
        radius: 4,
        maxRadius: 18 + (this.latestDisturbance / 3),
        alpha: 0.9,
        intensity: this.latestDisturbance,
        state: this.latestState,
        created: Date.now()
      });

      // Keep echo list bounded
      if (this.echoes.length > 25) {
        this.echoes.shift();
      }
    }
  }

  animate() {
    this.draw();
    this.sweepAngle = (this.sweepAngle + this.sweepSpeed) % (Math.PI * 2);
    requestAnimationFrame(() => this.animate());
  }

  draw() {
    const { ctx, width, height, cx, cy, maxRadius } = this;
    ctx.clearRect(0, 0, width, height);

    // 1. Polar Distance Arcs (1m, 2m, 3m, 4m)
    const rings = 4;
    for (let i = 1; i <= rings; i++) {
      const r = (maxRadius / rings) * i;
      ctx.beginPath();
      ctx.arc(cx, cy, r, -Math.PI * 0.85, -Math.PI * 0.15);
      ctx.strokeStyle = i === 2 ? 'rgba(0, 243, 255, 0.35)' : 'rgba(0, 243, 255, 0.12)';
      ctx.lineWidth = i === 2 ? 1.5 : 1;
      ctx.setLineDash(i % 2 === 0 ? [] : [4, 4]);
      ctx.stroke();
      ctx.setLineDash([]);

      // Distance labels
      ctx.fillStyle = 'rgba(126, 155, 184, 0.6)';
      ctx.font = '10px monospace';
      ctx.fillText(`${i}.0m`, cx + 8, cy - r + 12);
    }

    // 2. Azimuth Radials
    for (let angle = -Math.PI * 0.8; angle <= -Math.PI * 0.2; angle += Math.PI / 6) {
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(cx + Math.cos(angle) * maxRadius, cy + Math.sin(angle) * maxRadius);
      ctx.strokeStyle = 'rgba(0, 119, 255, 0.08)';
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    // 3. The Wall Barrier (Cross-Section at ~1.3m)
    const wallY = cy - (maxRadius * 0.35);
    ctx.beginPath();
    ctx.moveTo(cx - maxRadius * 0.8, wallY);
    ctx.lineTo(cx + maxRadius * 0.8, wallY);
    ctx.strokeStyle = 'rgba(255, 170, 0, 0.45)';
    ctx.lineWidth = 3;
    ctx.setLineDash([8, 4]);
    ctx.stroke();
    ctx.setLineDash([]);

    // Wall Label
    ctx.fillStyle = 'rgba(255, 170, 0, 0.85)';
    ctx.font = '9px monospace';
    ctx.fillText('/// DRYWALL / PARTITION BARRIER ///', cx - 95, wallY - 6);

    // 4. Fresnel Zone Multipath Corridor (Desktop to AP)
    const apY = cy - (maxRadius * 0.95);
    ctx.save();
    const grad = ctx.createRadialGradient(cx, (cy + apY) / 2, 10, cx, (cy + apY) / 2, maxRadius * 0.5);
    grad.addColorStop(0, 'rgba(0, 243, 255, 0.06)');
    grad.addColorStop(1, 'transparent');
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.ellipse(cx, (cy + apY) / 2, maxRadius * 0.38, (cy - apY) / 2, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    // 5. Remote AP Marker
    ctx.beginPath();
    ctx.arc(cx, apY, 7, 0, Math.PI * 2);
    ctx.fillStyle = '#0077ff';
    ctx.shadowColor = '#0077ff';
    ctx.shadowBlur = 12;
    ctx.fill();
    ctx.shadowBlur = 0;
    ctx.fillStyle = '#7e9bb8';
    ctx.font = '9px monospace';
    ctx.fillText('TELUS WI-FI MODEM (5 GHz)', cx + 12, apY + 3);

    // 6. Desktop Transceiver (Origin)
    ctx.beginPath();
    ctx.arc(cx, cy, 9, 0, Math.PI * 2);
    ctx.fillStyle = '#00f3ff';
    ctx.shadowColor = '#00f3ff';
    ctx.shadowBlur = 15;
    ctx.fill();
    ctx.shadowBlur = 0;
    ctx.fillStyle = '#00f3ff';
    ctx.font = '10px monospace';
    ctx.fillText('DESKTOP RADIO (RZ616)', cx - 62, cy + 22);

    // 7. Rotating Radar Sweep Beam
    const sweepStart = -Math.PI * 0.85;
    const sweepEnd = -Math.PI * 0.15;
    // Oscillate sweep angle across field of view
    const oscAngle = sweepStart + ((Math.sin(this.sweepAngle) + 1) / 2) * (sweepEnd - sweepStart);

    ctx.save();
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.arc(cx, cy, maxRadius, oscAngle - 0.18, oscAngle);
    ctx.closePath();
    const beamGrad = ctx.createRadialGradient(cx, cy, 5, cx, cy, maxRadius);
    beamGrad.addColorStop(0, 'rgba(0, 243, 255, 0.25)');
    beamGrad.addColorStop(1, 'transparent');
    ctx.fillStyle = beamGrad;
    ctx.fill();
    ctx.restore();

    // Leading sweep line
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(cx + Math.cos(oscAngle) * maxRadius, cy + Math.sin(oscAngle) * maxRadius);
    ctx.strokeStyle = 'rgba(0, 243, 255, 0.8)';
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // 8. Render Dynamic Through-Wall Echoes
    for (let i = this.echoes.length - 1; i >= 0; i--) {
      const e = this.echoes[i];
      e.radius += 0.4;
      e.alpha -= 0.015;

      if (e.alpha <= 0) {
        this.echoes.splice(i, 1);
        continue;
      }

      ctx.save();
      const isBreathing = e.state === 'BREATHING';
      const color = isBreathing ? '0, 255, 136' : (e.intensity > 55 ? '255, 51, 68' : '255, 170, 0');

      // Echo ripple circle
      ctx.beginPath();
      ctx.arc(e.x, e.y, e.radius, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(${color}, ${e.alpha})`;
      ctx.lineWidth = 2;
      ctx.stroke();

      // Echo central core blip
      ctx.beginPath();
      ctx.arc(e.x, e.y, 4, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${color}, ${e.alpha + 0.2})`;
      ctx.shadowColor = `rgba(${color}, 0.8)`;
      ctx.shadowBlur = 10;
      ctx.fill();

      // Target tag
      ctx.fillStyle = `rgba(${color}, ${e.alpha})`;
      ctx.font = '9px monospace';
      ctx.fillText(isBreathing ? 'HUMAN // RESPIRATION' : 'TARGET // MOTION', e.x + 8, e.y - 4);

      ctx.restore();
    }
  }
}

window.PolarRadar = PolarRadar;
