// ---------- Display: lightweight, safe markdown rendering ----------
// Escapes HTML first, then converts a small safe subset of markdown
// (bold, italic, inline code) into tags. Never trusts raw HTML from
// the model.
function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

export function renderMarkdownLite(text) {
  let out = escapeHtml(text);
  out = out.replace(/`([^`]+?)`/g, '<code>$1</code>');
  out = out.replace(/\*\*([^*]+?)\*\*/g, '<strong>$1</strong>');
  out = out.replace(/__([^_]+?)__/g, '<strong>$1</strong>');
  out = out.replace(/\*([^*]+?)\*/g, '<em>$1</em>');
  out = out.replace(/(?<!\w)_([^_]+?)_(?!\w)/g, '<em>$1</em>');
  return out;
}

// ---------- Speech: strip markdown syntax and emoji ----------
// Removes markdown formatting characters (so "**bold**" isn't read as
// "asterisk asterisk bold asterisk asterisk") and strips emoji so the
// speech synthesizer only reads actual words.
const EMOJI_PATTERN =
  /[\u{1F1E6}-\u{1F1FF}\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{2190}-\u{21FF}\u{2B00}-\u{2BFF}\u{2300}-\u{23FF}\u{FE0F}\u{200D}]/gu;

export function prepareForSpeech(text) {
  let out = text;
  // Emoji first, before punctuation cleanup collapses whitespace around them.
  out = out.replace(EMOJI_PATTERN, '');
  // Markdown syntax markers: bold/italic asterisks & underscores, inline
  // code backticks, headings, blockquote markers, strikethrough.
  out = out.replace(/\*\*/g, '');
  out = out.replace(/\*/g, '');
  out = out.replace(/`/g, '');
  out = out.replace(/~~/g, '');
  out = out.replace(/^\s{0,3}#{1,6}\s+/gm, '');
  out = out.replace(/^\s{0,3}>\s?/gm, '');
  out = out.replace(/^\s*[-*+]\s+/gm, '');
  // Collapse leftover doubled/trailing whitespace created by stripping.
  out = out.replace(/[ \t]{2,}/g, ' ').replace(/\n{3,}/g, '\n\n').trim();
  return out;
}
