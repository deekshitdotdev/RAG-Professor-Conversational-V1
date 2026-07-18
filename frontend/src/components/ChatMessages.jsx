import React, { useEffect, useRef, useState } from 'react';
import Message from './Message.jsx';
import LogoMark from './LogoMark.jsx';
import { prepareForSpeech } from '../textUtils.js';

export default function ChatMessages({ messages, documentName }) {
  const scrollRef = useRef(null);
  const [readingId, setReadingId] = useState(null);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages]);

  useEffect(() => {
    // Stop any speech in progress if the component unmounts.
    return () => speechSynthesis.cancel();
  }, []);

  const handleToggleRead = (id, text) => {
    if (readingId === id) {
      speechSynthesis.cancel();
      setReadingId(null);
      return;
    }
    speechSynthesis.cancel();
    const utter = new SpeechSynthesisUtterance(prepareForSpeech(text));
    utter.onend = () => setReadingId((cur) => (cur === id ? null : cur));
    setReadingId(id);
    speechSynthesis.speak(utter);
  };

  return (
    <div className="chat-scroll" ref={scrollRef}>
      <div className="chat-inner">
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="glyph"><LogoMark size={40} /></div>
            {documentName ? (
              <>
                <h2>Ready — ask about {documentName}</h2>
                <p>Try: "Summarize this document" or "What does it say about X?"</p>
              </>
            ) : (
              <>
                <h2>Upload a document to begin</h2>
                <p>Docbench reads your PDF or TXT file entirely on this machine, then answers questions about it with page-cited excerpts. Nothing leaves your computer.</p>
              </>
            )}
          </div>
        ) : (
          messages.map((m) => (
            <Message
              key={m.id}
              id={m.id}
              role={m.role}
              text={m.text}
              citations={m.citations}
              error={m.error}
              streaming={m.streaming}
              isReading={readingId === m.id}
              onToggleRead={handleToggleRead}
            />
          ))
        )}
      </div>
    </div>
  );
}
