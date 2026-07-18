// Safely parse a fetch Response as JSON even if the server returned plain
// text (e.g. a proxy error, or an exception that slipped past the handler).
// Prevents "Unexpected token ... is not valid JSON" from crashing the UI.
export async function safeJson(resp) {
  const raw = await resp.text();
  try {
    return JSON.parse(raw);
  } catch (e) {
    return { detail: raw || `Server returned ${resp.status} with no readable body.` };
  }
}

export async function uploadDocument(file) {
  const form = new FormData();
  form.append('file', file);
  const resp = await fetch('/api/upload', { method: 'POST', body: form });
  const data = await safeJson(resp);
  if (!resp.ok) throw new Error(data.detail || `Upload failed (${resp.status})`);
  return data;
}

export async function removeDocument() {
  return fetch('/api/document', { method: 'DELETE' });
}

export async function fetchModels() {
  const resp = await fetch('/api/models');
  const data = await safeJson(resp);
  if (!resp.ok) throw new Error(data.detail || 'Failed to load models');
  return data;
}

export async function setModel(role, model) {
  return fetch('/api/model', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ role, model })
  });
}

export async function fetchHistory() {
  const resp = await fetch('/api/history');
  return resp.json();
}

export async function clearHistory() {
  return fetch('/api/history', { method: 'DELETE' });
}

export async function fetchStatus() {
  const resp = await fetch('/api/status');
  return resp.json();
}

// Streams NDJSON events from /api/ask. Calls onEvent(event) for each parsed
// line and resolves once the stream ends. Malformed chunks are skipped
// rather than crashing the whole stream.
export async function streamAsk(query, onEvent) {
  const resp = await fetch('/api/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query })
  });

  if (!resp.ok) {
    const err = await safeJson(resp);
    throw new Error(err.detail || 'Request failed');
  }

  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop();

    for (const line of lines) {
      if (!line.trim()) continue;
      let event;
      try {
        event = JSON.parse(line);
      } catch (e) {
        continue;
      }
      onEvent(event);
    }
  }
}
