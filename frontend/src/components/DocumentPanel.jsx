import React, { useRef, useState } from 'react';

export default function DocumentPanel({ document, onUpload, onRemove }) {
  const fileInputRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const [statusLabel, setStatusLabel] = useState(null); // e.g. "Indexing foo.pdf…"

  const handleFiles = async (file) => {
    if (!file) return;
    setStatusLabel(`Indexing ${file.name}…`);
    try {
      await onUpload(file);
    } catch (err) {
      alert(err.message);
    } finally {
      setStatusLabel(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <div>
      <div className="section-label">Document</div>
      <div
        className={`dropzone${dragging ? ' drag' : ''}`}
        onClick={(e) => { if (e.target !== fileInputRef.current) fileInputRef.current.click(); }}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={(e) => { e.preventDefault(); setDragging(false); }}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          handleFiles(e.dataTransfer.files[0]);
        }}
      >
        <span>
          {statusLabel ? statusLabel : (<>Drop a PDF or TXT here<br />or click to browse</>)}
        </span>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.txt"
          style={{ display: 'none' }}
          onChange={(e) => handleFiles(e.target.files[0])}
        />
      </div>

      {document && (
        <div className="doc-card show" style={{ marginTop: 10 }}>
          <div className="name">{document.file_name}</div>
          <div className="stats">
            <span>{document.pages} pages</span>
            <span>{document.chunks} chunks</span>
            {document.ocr_pages ? <span>{document.ocr_pages} OCR'd</span> : null}
            {document.chunk_seconds != null && document.embed_seconds != null && (
              <span>chunk {document.chunk_seconds}s / embed {document.embed_seconds}s</span>
            )}
            {document.chunk_seconds == null && document.embed_seconds != null && (
              <span>embed {document.embed_seconds}s</span>
            )}
          </div>
          <button onClick={onRemove}>Remove document</button>
        </div>
      )}
    </div>
  );
}
