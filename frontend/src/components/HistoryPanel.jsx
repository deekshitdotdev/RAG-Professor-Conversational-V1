import React from 'react';

export default function HistoryPanel({ history, onSelect, onClear }) {
  // Keep each item's original index (position in the flat history array) so
  // the parent can reconstruct the whole conversation up to that point, not
  // just refill the question text box.
  const items = history.map((h, i) => ({ ...h, _index: i })).reverse();

  return (
    <div style={{ display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0 }}>
      <div className="section-label" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span>History</span>
        <button className="clear-history" onClick={onClear}>clear</button>
      </div>
      <div className="history-list">
        {items.map((h) => (
          <button key={h._index} className="history-item" title={h.query} onClick={() => onSelect(h._index)}>
            {h.query}
          </button>
        ))}
      </div>
    </div>
  );
}
