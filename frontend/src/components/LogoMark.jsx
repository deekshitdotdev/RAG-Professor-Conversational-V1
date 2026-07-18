import React from 'react';

// A small terminal-prompt glyph in a rounded square — reads as "local /
// offline tool" rather than a generic chat bubble or robot icon.
export default function LogoMark({ size = 22 }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 40 40"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      style={{ flexShrink: 0 }}
    >
      <rect x="1" y="1" width="38" height="38" rx="9" fill="#1a232d" stroke="#2e7d76" strokeWidth="2" />
      <path d="M11 14 L18 20 L11 26" stroke="#4fd1c5" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" fill="none" />
      <line x1="21" y1="26" x2="29" y2="26" stroke="#4fd1c5" strokeWidth="3" strokeLinecap="round" />
    </svg>
  );
}
