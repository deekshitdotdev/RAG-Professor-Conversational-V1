import React from 'react';
import DocumentPanel from './DocumentPanel.jsx';
import ModelSelects from './ModelSelects.jsx';
import SystemMeters from './SystemMeters.jsx';
import HistoryPanel from './HistoryPanel.jsx';
import LogoMark from './LogoMark.jsx';

export default function Sidebar({
  document, onUpload, onRemove,
  modelData, onSetModel,
  status,
  history, onSelectHistory, onClearHistory
}) {
  return (
    <div className="sidebar">
      <div className="brand-row">
        <LogoMark size={22} />
        <div className="brand">Deekshi <span>Assitant</span></div>
      </div>
      <DocumentPanel document={document} onUpload={onUpload} onRemove={onRemove} />
      <ModelSelects modelData={modelData} onSetModel={onSetModel} />
      <SystemMeters status={status} />
      <HistoryPanel history={history} onSelect={onSelectHistory} onClear={onClearHistory} />
    </div>
  );
}
