import React from 'react';

function Meter({ label, percent, valueLabel }) {
  const pct = percent == null ? 0 : Math.min(100, percent);
  let fillClass = 'meter-fill';
  if (percent > 90) fillClass += ' danger';
  else if (percent > 70) fillClass += ' warn';

  return (
    <div className="meter-row">
      <div className="meter-label">{label}</div>
      <div className="meter-track"><div className={fillClass} style={{ width: `${pct}%` }} /></div>
      <div className="meter-val">{valueLabel}</div>
    </div>
  );
}

export default function SystemMeters({ status }) {
  const sys = status?.system;
  const cpu = sys?.cpu_ram?.cpu_percent;
  const ram = sys?.cpu_ram?.ram_percent;
  const gpu = sys?.gpu;
  const vramPct = gpu?.available ? (gpu.vram_used_mb / gpu.vram_total_mb) * 100 : null;

  return (
    <div>
      <div className="section-label">System</div>
      <Meter label="CPU" percent={cpu} valueLabel={cpu != null ? `${cpu.toFixed(0)}%` : '—'} />
      <Meter label="RAM" percent={ram} valueLabel={ram != null ? `${ram.toFixed(0)}%` : '—'} />
      <Meter
        label="GPU"
        percent={gpu?.available ? gpu.gpu_util_percent : null}
        valueLabel={gpu?.available ? `${gpu.gpu_util_percent.toFixed(0)}%` : 'n/a'}
      />
      <Meter
        label="VRAM"
        percent={vramPct}
        valueLabel={gpu?.available ? `${(gpu.vram_used_mb / 1024).toFixed(1)}G` : 'n/a'}
      />
      <div className="status-line">
        <div className={`dot${status?.ollama?.available ? ' ok' : ''}`} />
        <span>{status?.ollama?.available ? `${status.ollama.model} ready` : (status?.ollama?.message || 'checking Ollama…')}</span>
      </div>
    </div>
  );
}
