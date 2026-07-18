import React, { useEffect, useRef, useState } from 'react';

const SpeechRecognitionApi =
  typeof window !== 'undefined' ? (window.SpeechRecognition || window.webkitSpeechRecognition) : null;

export default function InputBar({ value, onChange, onSend, disabled, sending, modelHint, focusSignal }) {
  const textareaRef = useRef(null);
  const recognitionRef = useRef(null);
  const baseValueRef = useRef('');
  const [listening, setListening] = useState(false);

  useEffect(() => {
    if (focusSignal) textareaRef.current?.focus();
  }, [focusSignal]);

  const resizeTextarea = () => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = 'auto';
      el.style.height = Math.min(el.scrollHeight, 160) + 'px';
    }
  };

  const handleInput = (e) => {
    onChange(e.target.value);
    resizeTextarea();
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  useEffect(() => {
    return () => {
      if (recognitionRef.current) recognitionRef.current.stop();
    };
  }, []);

  const toggleMic = () => {
    if (!SpeechRecognitionApi) return;

    if (listening) {
      recognitionRef.current?.stop();
      return;
    }

    const recognition = new SpeechRecognitionApi();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    baseValueRef.current = value;

    recognition.onresult = (event) => {
      let transcript = '';
      for (let i = 0; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      const combined = baseValueRef.current
        ? `${baseValueRef.current} ${transcript}`
        : transcript;
      onChange(combined);
      requestAnimationFrame(resizeTextarea);
    };

    recognition.onerror = () => setListening(false);
    recognition.onend = () => setListening(false);

    recognitionRef.current = recognition;
    setListening(true);
    recognition.start();
  };

  return (
    <div className="input-bar">
      <div className="input-inner">
        <textarea
          ref={textareaRef}
          rows={1}
          placeholder="Ask something about the document…"
          value={value}
          disabled={disabled}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
        />
        <button
          type="button"
          className={`mic${listening ? ' listening' : ''}`}
          onClick={toggleMic}
          disabled={disabled || !SpeechRecognitionApi}
          title={SpeechRecognitionApi ? (listening ? 'Stop dictation' : 'Speak your question') : 'Speech input not supported in this browser'}
        >
          🎤
        </button>
        <button className="send" onClick={onSend} disabled={disabled || sending || !value.trim()}>
          Ask
        </button>
      </div>
      <div className="hint">model: {modelHint || '—'}{listening ? ' · listening…' : ''}</div>
    </div>
  );
}
