import React, { useEffect, useRef, useState } from 'react';
import Sidebar from './components/Sidebar.jsx';
import ChatMessages from './components/ChatMessages.jsx';
import ConversationActions from './components/ConversationActions.jsx';
import InputBar from './components/InputBar.jsx';
import {
  uploadDocument, removeDocument, fetchModels, setModel as setModelApi,
  fetchHistory, clearHistory as clearHistoryApi, fetchStatus, streamAsk
} from './api.js';

let nextId = 1;

export default function App() {
  const [document, setDocument] = useState(null);
  const [modelData, setModelData] = useState(null);
  const [status, setStatus] = useState(null);
  const [history, setHistory] = useState([]);
  const [messages, setMessages] = useState([]);
  const [query, setQuery] = useState('');
  const [sending, setSending] = useState(false);
  const [focusSignal, setFocusSignal] = useState(0);

  const statusIntervalRef = useRef(null);

  const loadModels = async () => {
    try {
      const data = await fetchModels();
      setModelData(data);
    } catch (e) { /* Ollama not reachable yet, status poll will surface it */ }
  };

  const loadHistory = async () => {
    try {
      const data = await fetchHistory();
      setHistory(data);
    } catch (e) { /* ignore */ }
  };

  const pollStatus = async () => {
    try {
      const data = await fetchStatus();
      setStatus(data);
      if (data.current_document && !document) {
        setDocument(data.current_document);
      }
    } catch (e) { /* backend not up yet */ }
  };

  useEffect(() => {
    pollStatus();
    loadHistory();
    loadModels();
    statusIntervalRef.current = setInterval(pollStatus, 3000);
    return () => clearInterval(statusIntervalRef.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleUpload = async (file) => {
    const data = await uploadDocument(file);
    setDocument(data);
    setFocusSignal((n) => n + 1);
  };

  const handleRemove = async () => {
    await removeDocument();
    setDocument(null);
  };

  const handleSetModel = async (role, model) => {
    await setModelApi(role, model);
    setModelData((prev) => prev ? { ...prev, [role === 'chat' ? 'chat_model' : 'vision_model']: model } : prev);
    pollStatus();
  };

  const handleClearHistory = async () => {
    await clearHistoryApi();
    loadHistory();
  };

  const handleSelectHistory = (index) => {
    const clicked = history[index];
    if (!clicked) return;

    // Walk backwards to the start of this "conversation" - i.e. as far back
    // as the document stays the same. A different document means it was a
    // separate session, so we stop there rather than mixing threads.
    let start = index;
    while (start > 0 && history[start - 1].document === clicked.document) {
      start -= 1;
    }

    const thread = history.slice(start, index + 1);
    const rebuilt = [];
    thread.forEach((h) => {
      rebuilt.push({ id: nextId++, role: 'user', text: h.query });
      rebuilt.push({
        id: nextId++,
        role: 'assistant',
        text: h.answer || '',
        citations: h.citations || [],
      });
    });

    setMessages(rebuilt);
    setQuery('');
  };

  const handleSend = async () => {
    const q = query.trim();
    if (!q || !document || sending) return;
    setQuery('');
    setSending(true);

    const userMsg = { id: nextId++, role: 'user', text: q };
    const assistantMsg = { id: nextId++, role: 'assistant', text: '', citations: [], streaming: true };
    setMessages((prev) => [...prev, userMsg, assistantMsg]);

    try {
      await streamAsk(q, (event) => {
        if (event.type === 'citations' && event.data.length) {
          setMessages((prev) => prev.map((m) =>
            m.id === assistantMsg.id ? { ...m, citations: event.data } : m
          ));
        } else if (event.type === 'token') {
          setMessages((prev) => prev.map((m) =>
            m.id === assistantMsg.id ? { ...m, text: m.text + event.data } : m
          ));
        } else if (event.type === 'error') {
          setMessages((prev) => prev.map((m) =>
            m.id === assistantMsg.id ? { ...m, error: event.data, streaming: false } : m
          ));
        }
      });
      setMessages((prev) => prev.map((m) =>
        m.id === assistantMsg.id ? { ...m, streaming: false } : m
      ));
      loadHistory();
    } catch (err) {
      setMessages((prev) => prev.map((m) =>
        m.id === assistantMsg.id ? { ...m, error: `Connection error: ${err.message}`, streaming: false } : m
      ));
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="app">
      <Sidebar
        document={document}
        onUpload={handleUpload}
        onRemove={handleRemove}
        modelData={modelData}
        onSetModel={handleSetModel}
        status={status}
        history={history}
        onSelectHistory={handleSelectHistory}
        onClearHistory={handleClearHistory}
      />
      <div className="main">
        <ChatMessages messages={messages} documentName={document?.file_name} />
        <ConversationActions messages={messages} />
        <InputBar
          value={query}
          onChange={setQuery}
          onSend={handleSend}
          disabled={!document}
          sending={sending}
          modelHint={status?.ollama?.model}
          focusSignal={focusSignal}
        />
      </div>
    </div>
  );
}
