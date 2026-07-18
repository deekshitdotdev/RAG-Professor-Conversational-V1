import React from 'react';

function buildOptions(installed, current, recommended) {
  const options = installed && installed.length ? installed : [current, recommended].filter(Boolean);
  const unique = [...new Set(options)];
  if (current && !unique.includes(current)) unique.unshift(current);
  return unique;
}

export default function ModelSelects({ modelData, onSetModel }) {
  const chatOptions = buildOptions(
    modelData?.installed, modelData?.chat_model, modelData?.recommended_chat
  );
  const visionOptions = buildOptions(
    modelData?.installed, modelData?.vision_model, modelData?.recommended_vision
  );

  return (
    <div>
      <div className="section-label">Models</div>
      <div style={{ fontSize: 11.5, color: 'var(--text-dim)', marginBottom: 4 }}>Chat / code / math</div>
      <select
        className="model-select"
        value={modelData?.chat_model || ''}
        onChange={(e) => onSetModel('chat', e.target.value)}
      >
        {chatOptions.map((name) => (
          <option key={name} value={name}>
            {name}
            {name === modelData?.recommended_chat ? ' (recommended)' : ''}
            {name === modelData?.chat_model && !chatOptions.includes(name) ? ' (not pulled yet)' : ''}
          </option>
        ))}
      </select>

      <div style={{ fontSize: 11.5, color: 'var(--text-dim)', margin: '8px 0 4px' }}>
        Vision / OCR (auto-used for scanned PDFs)
      </div>
      <select
        className="model-select"
        value={modelData?.vision_model || ''}
        onChange={(e) => onSetModel('vision', e.target.value)}
      >
        {visionOptions.map((name) => (
          <option key={name} value={name}>
            {name}
            {name === modelData?.recommended_vision ? ' (recommended)' : ''}
          </option>
        ))}
      </select>
    </div>
  );
}
