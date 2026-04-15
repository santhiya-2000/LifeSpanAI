INTERACTIVE_GAUGE_HTML = """
<!DOCTYPE html>
<html>
<head>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: Arial, sans-serif; background: transparent; padding: 10px; }
  .container { display: flex; flex-direction: column; align-items: center; gap: 10px; }
  canvas { display: block; }
  .slider-row { display: flex; align-items: center; gap: 10px; width: 260px; }
  .slider-row label { font-size: 12px; color: #6b7280; white-space: nowrap; }
  input[type=range] {
    flex: 1; -webkit-appearance: none; height: 4px;
    border-radius: 2px; background: #e5e7eb; outline: none;
  }
  input[type=range]::-webkit-slider-thumb {
    -webkit-appearance: none; width: 16px; height: 16px;
    border-radius: 50%; background: #1E2761; cursor: pointer;
  }
  .rul-display { font-size: 13px; font-weight: 600; min-width: 28px; text-align: right; }
  .status-pill {
    padding: 4px 16px; border-radius: 20px;
    font-size: 12px; font-weight: 600; letter-spacing: 0.05em;
  }
  .rec-box {
    width: 260px; padding: 10px 14px; border-radius: 8px;
    font-size: 12px; line-height: 1.5; border-left: 4px solid;
  }
</style>
</head>
<body>
<div class="container">
  <canvas id="gauge" width="260" height="145"></canvas>
  <div class="slider-row">
    <label>RUL</label>
    <input type="range" id="slider" min="0" max="125" step="1" value="INITIAL_RUL">
    <span class="rul-display" id="rulNum">INITIAL_RUL</span>
  </div>
  <div class="status-pill" id="pill"></div>
  <div class="rec-box" id="rec"></div>
</div>

<script>
const slider = document.getElementById('slider');
const rulNum = document.getElementById('rulNum');
const pill   = document.getElementById('pill');
const rec    = document.getElementById('rec');
const canvas = document.getElementById('gauge');
const ctx    = canvas.getContext('2d');

function getColor(rul) {
  if (rul <= 20) return '#DC2626';
  if (rul <= 60) return '#F59E0B';
  return '#10B981';
}

function getStatus(rul) {
  if (rul <= 20) return { label: 'CRITICAL', bg: '#FEE2E2', color: '#991B1B' };
  if (rul <= 60) return { label: 'WARNING',  bg: '#FEF3C7', color: '#92400E' };
  return               { label: 'HEALTHY',   bg: '#D1FAE5', color: '#065F46' };
}

function getRec(rul) {
  if (rul <= 10) return {
    msg: 'Immediate shutdown required. Failure imminent.',
    bg: '#FEE2E2', border: '#DC2626', color: '#991B1B'
  };
  if (rul <= 20) return {
    msg: `Only ${rul} cycles left. Schedule maintenance within 5 cycles.`,
    bg: '#FEE2E2', border: '#DC2626', color: '#991B1B'
  };
  if (rul <= 60) return {
    msg: `${rul} cycles remaining. Plan maintenance in next scheduled window.`,
    bg: '#FEF3C7', border: '#F59E0B', color: '#92400E'
  };
  return {
    msg: `Engine healthy with ${rul} cycles remaining. Continue normal operations.`,
    bg: '#D1FAE5', border: '#10B981', color: '#065F46'
  };
}

function drawGauge(rul) {
  ctx.clearRect(0, 0, 260, 145);
  const cx = 130, cy = 122, r = 90;

  // Background arc
  ctx.beginPath();
  ctx.arc(cx, cy, r, Math.PI, 0);
  ctx.lineWidth = 20;
  ctx.strokeStyle = '#f3f4f6';
  ctx.lineCap = 'round';
  ctx.stroke();

  // Zone arcs
  const zones = [
    { start: Math.PI,        end: Math.PI * 1.16, color: '#DC2626' },
    { start: Math.PI * 1.16, end: Math.PI * 1.48, color: '#F59E0B' },
    { start: Math.PI * 1.48, end: Math.PI * 2,    color: '#10B981' },
  ];
  zones.forEach(z => {
    ctx.beginPath();
    ctx.arc(cx, cy, r, z.start, z.end);
    ctx.lineWidth = 20;
    ctx.strokeStyle = z.color;
    ctx.lineCap = 'butt';
    ctx.globalAlpha = 0.82;
    ctx.stroke();
    ctx.globalAlpha = 1;
  });

  // Needle
  const pct   = Math.min(rul / 125, 1);
  const angle = Math.PI + pct * Math.PI;
  const nx    = cx + (r - 2) * Math.cos(angle);
  const ny    = cy + (r - 2) * Math.sin(angle);
  const color = getColor(rul);

  ctx.beginPath();
  ctx.moveTo(cx, cy);
  ctx.lineTo(nx, ny);
  ctx.lineWidth   = 3;
  ctx.strokeStyle = color;
  ctx.lineCap     = 'round';
  ctx.stroke();

  // Needle hub
  ctx.beginPath();
  ctx.arc(cx, cy, 7, 0, Math.PI * 2);
  ctx.fillStyle = color;
  ctx.fill();

  // RUL number
  ctx.fillStyle = color;
  ctx.font      = 'bold 30px Arial';
  ctx.textAlign = 'center';
  ctx.fillText(rul, cx, cy - 26);

  ctx.fillStyle = '#6b7280';
  ctx.font      = '11px Arial';
  ctx.fillText('cycles remaining', cx, cy - 10);

  // Zone labels
  ctx.fillStyle = '#DC2626';
  ctx.font      = '10px Arial';
  ctx.textAlign = 'left';
  ctx.fillText('0', 26, cy + 6);

  ctx.fillStyle = '#10B981';
  ctx.textAlign = 'right';
  ctx.fillText('125', 234, cy + 6);
}

function update(rul) {
  rul = parseInt(rul);
  drawGauge(rul);
  rulNum.textContent = rul;

  const st = getStatus(rul);
  pill.textContent        = st.label;
  pill.style.background   = st.bg;
  pill.style.color        = st.color;

  const r = getRec(rul);
  rec.textContent         = r.msg;
  rec.style.background    = r.bg;
  rec.style.borderColor   = r.border;
  rec.style.color         = r.color;
}

slider.oninput = e => update(e.target.value);
update(slider.value);
</script>
</body>
</html>
"""

def get_gauge_html(rul_value):
    return INTERACTIVE_GAUGE_HTML.replace("INITIAL_RUL", str(int(rul_value)))