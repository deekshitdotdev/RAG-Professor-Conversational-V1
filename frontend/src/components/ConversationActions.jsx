import React, { useState } from 'react';

function buildTranscript(messages) {
  return messages
    .filter((m) => !m.error)
    .map((m) => `${m.role === 'user' ? 'You' : 'AI'}: ${m.text}`)
    .join('\n\n');
}

export default function ConversationActions({ messages }) {
  const [copied, setCopied] = useState(false);
  const hasContent = messages.some((m) => !m.error && m.text);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(buildTranscript(messages));
    setCopied(true);
    setTimeout(() => setCopied(false), 1200);
  };

  return (
    <div className="conversation-actions">
      <div className="conversation-actions-inner">
        <span className="hint-label">whole conversation</span>
        <button onClick={handleCopy} disabled={!hasContent}>
          {copied ? '✓ Copied' : '⧉ Copy entire conversation'}
        </button>
      </div>
    </div>
  );
}
