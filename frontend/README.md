# Docbench (React)

A React + Vite rebuild of the Docbench offline document assistant UI.

## What changed from the original single HTML file

- Split into components (`Sidebar`, `DocumentPanel`, `ModelSelects`, `SystemMeters`,
  `HistoryPanel`, `ChatMessages`, `Message`, `ConversationActions`, `InputBar`, `LogoMark`).
- **Copy** and **Read aloud** appear below each individual AI reply, same as
  the original. Read aloud strips markdown symbols (`*`, `` ` ``, `#`, etc.)
  and emoji before speaking, so it never reads out stray punctuation —
  emoji still display normally in the chat, they're just skipped by speech.
- A second **Copy entire conversation** button sits in its own bar just
  above the input box, for grabbing the full You/AI transcript at once.
- Assistant replies render a small safe subset of markdown (`**bold**`,
  `*italic*`, `` `code` ``) instead of showing literal asterisks/backticks.
- The input box has a **mic button** for speech-to-text dictation (Web
  Speech API — Chrome/Edge support it, Safari partially, Firefox does not;
  the button disables itself with a tooltip when unsupported). Pressing
  Enter still sends the message, whether typed or dictated.
- The input box is disabled until a document finishes uploading (chunking +
  embedding), and auto-focuses right after, matching the original.
- A small terminal-prompt logo mark sits next to the "docbench" title, in
  the empty state, and as the browser tab favicon.
- All `/api/*` calls (`upload`, `document`, `models`, `model`, `history`,
  `status`, `ask`) are preserved exactly as in the original, including the
  NDJSON streaming parser for `/api/ask`.

## Requirements

This is a frontend only. It expects a backend server (the same one the
original HTML file talked to) exposing:

```
POST   /api/upload      (multipart form, field "file")
DELETE /api/document
GET    /api/models
POST   /api/model        { role, model }
GET    /api/history
DELETE /api/history
GET    /api/status
POST   /api/ask          { query }  -> NDJSON stream of
                                        {type:"citations"|"token"|"error", data}
```

## Run it

```bash
npm install
npm run dev
```

By default, `vite.config.js` proxies `/api/*` requests to
`http://localhost:8000`. Edit the `target` in `vite.config.js` if your
backend runs elsewhere.

To build for production:

```bash
npm run build
npm run preview
```
