import React, { useState } from 'react';
import { renderMarkdownLite } from '../textUtils.js';

export default function Message({ id, role, text, citations, error, streaming, isReading, onToggleRead }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1200);
  };

  const showActions = role === 'assistant' && !streaming && !error && text;

  return (
    <div className={`msg ${role}`}>
      <div className="role-tag">{role === 'user' ? 'you' : 'ai'}</div>
      <div style={{ flex: 1 }}>
        {error ? (
          <div className="error-box">{error}</div>
        ) : (
          <div
            className={`msg-body${streaming ? ' cursor-blink' : ''}`}
            dangerouslySetInnerHTML={{ __html: renderMarkdownLite(text) }}
          />
        )}
        {citations && citations.length > 0 && (
          <div className="citations">
            {citations.map((c, i) => (
              <span className="citation-chip" key={i} title={c.preview}>
                p.{c.page}{c.heading ? ` · ${c.heading}` : ''}
              </span>
            ))}
          </div>
        )}
        {showActions && (
          <div className="msg-actions">
            <button onClick={handleCopy}>{copied ? '✓ Copied' : '⧉ Copy'}</button>
            <button
              className={isReading ? 'active' : ''}
              onClick={() => onToggleRead(id, text)}
            >
              {isReading ? '■ Stop' : '▶ Read aloud'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
