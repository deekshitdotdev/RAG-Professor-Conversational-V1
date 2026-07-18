# RAG-Professor Conversational V1 — Offline Document Assistant with Memory
# RAG-Professor 对话版 V1 — 具备记忆功能的离线文档助手

Upload a PDF or TXT document, ask questions, and have natural multi-turn
conversations with your documents.

RAG-Professor combines Retrieval Augmented Generation (RAG), vector search,
BM25 hybrid retrieval, local LLMs, and conversational memory to provide
context-aware answers with citations — entirely on your own machine.

No internet connection is required during usage after the initial setup.

上传一份 PDF 或 TXT 文档，即可提问并与文档进行自然的多轮对话。

RAG-Professor 结合了检索增强生成（RAG）、向量搜索、BM25 混合检索、
本地大语言模型以及对话记忆，完全在你自己的电脑上提供带引用来源的
上下文感知回答。

完成初始设置后，使用过程无需联网。

Features / 功能特性:
- PDF/TXT document understanding / PDF/TXT 文档理解
- Streaming AI responses / AI 回答流式输出
- Page-level citations / 页码级引用
- Chat history persistence / 聊天记录持久化保存
- Follow-up question understanding / 理解追问（后续问题）
- Conversation memory / 对话记忆
- Previous conversation restoration / 恢复历史对话
- Local LLM inference using Ollama / 使用 Ollama 进行本地大模型推理
- Docker Compose deployment support / 支持 Docker Compose 部署
- English and Chinese (中文) language support / 支持英文和中文

Runs on everything from CPU-only laptops to gaming PCs with dedicated GPUs.
Choose the model that matches your hardware.

可在纯 CPU 笔记本电脑到配备独立显卡的游戏 PC 上运行，请根据你的硬件
选择合适的模型。

## Version History / 版本历史

### Conversational V1 🚀

Added:
- Persistent chat history
- Conversation memory
- Context-aware follow-up questions
- Automatic continuation for truncated LLM responses
- Docker Compose deployment
- Improved history restoration
- Better Ollama integration
- Chinese (中文) language support for documents and UI

新增内容：
- 持久化聊天记录
- 对话记忆
- 支持上下文感知的追问
- 自动续写被截断的模型回答
- Docker Compose 部署支持
- 改进的历史记录恢复功能
- 更好的 Ollama 集成
- 文档与界面的中文语言支持

### Initial Version / 初始版本
- PDF/TXT ingestion / PDF/TXT 文档导入
- Vector search / 向量搜索
- Local LLM support / 支持本地大语言模型
- ChromaDB retrieval / ChromaDB 检索

---

## 1. System Requirements & Model Recommendations / 系统要求与模型推荐

### Minimum Requirements
- Windows 10/11, Linux, or macOS
- 8 GB RAM (16 GB recommended)
- Dual-core CPU or better
- 5 GB free disk space
- Ollama installed

### No GPU? No Problem

RAG-Professor works perfectly on CPU-only systems. If your computer does
not have an NVIDIA RTX GPU, AMD GPU, or other dedicated graphics card,
simply use a smaller Ollama model such as:

```bash
ollama pull qwen3:4b
```

Recommended CPU-friendly models:

| Model      | Recommended For                   |
|------------|------------------------------------|
| qwen3:4b   | Best balance of speed and quality |
| gemma3:4b  | Lightweight and efficient         |
| qwen3:1.7b | Very low-end systems               |
| phi4-mini  | Fast responses with low RAM usage |

For CPU-only machines:
```env
LLM_MODEL=qwen3:4b
```

### Recommended Requirements

For the best experience:
- 16 GB RAM
- NVIDIA RTX GPU (6 GB+ VRAM)
- Intel i5/Ryzen 5 or better

Recommended model:
```bash
ollama pull qwen3:8b
```
```env
LLM_MODEL=qwen3:8b
```

This provides significantly better reasoning, explanations, and document
understanding.

### High-End Systems

If you have an RTX 4070 / 4080 / 4090 and 32 GB+ RAM, you can experiment
with larger models:

```bash
ollama pull qwen2.5:14b
```
or
```bash
ollama pull deepseek-r1:14b
```

These models generally produce higher-quality answers but require
substantially more memory.

### Suggested Models by Hardware

| Hardware                 | Recommended Model         |
|---------------------------|----------------------------|
| 8 GB RAM, No GPU          | qwen3:1.7b                |
| 8–16 GB RAM, No GPU       | qwen3:4b                  |
| 16 GB RAM + RTX 3050 6GB  | qwen3:8b                  |
| 16 GB RAM + RTX 4060+     | qwen3:8b / DeepSeek-R1 8B |
| 32 GB RAM + RTX 4070+     | qwen2.5:14b               |
| 64 GB RAM + High-End GPU  | DeepSeek-R1 14B+          |

### 系统要求（中文说明）

**最低要求：**
- Windows 10/11、Linux 或 macOS
- 8 GB 内存（推荐 16 GB）
- 双核 CPU 或更高
- 5 GB 可用磁盘空间
- 已安装 Ollama

**没有 GPU？没问题**

RAG-Professor 在纯 CPU 系统上也能完美运行。如果你的电脑没有 NVIDIA RTX、
AMD 或其他独立显卡，只需使用较小的 Ollama 模型，例如：
```bash
ollama pull qwen3:4b
```

**推荐配置（更好的体验）：**
- 16 GB 内存
- NVIDIA RTX 显卡（6 GB 及以上显存）
- Intel i5 / Ryzen 5 或更高

**高端系统：**

如果你有 RTX 4070 / 4080 / 4090 及 32 GB 以上内存，可以尝试更大的模型，
如 `qwen2.5:14b` 或 `deepseek-r1:14b`，这些模型效果更好，但需要更多显存和内存。

**按硬件推荐模型：**

| 硬件配置 | 推荐模型 |
|---|---|
| 8 GB 内存，无 GPU | qwen3:1.7b |
| 8–16 GB 内存，无 GPU | qwen3:4b |
| 16 GB 内存 + RTX 3050 6GB | qwen3:8b |
| 16 GB 内存 + RTX 4060 及以上 | qwen3:8b / DeepSeek-R1 8B |
| 32 GB 内存 + RTX 4070 及以上 | qwen2.5:14b |
| 64 GB 内存 + 高端显卡 | DeepSeek-R1 14B+ |

---

## Docker Support 🐳 / Docker 支持 🐳

RAG-Professor can run completely through Docker Compose.

The application contains:
- FastAPI backend container
- React frontend container
- Automatic internal networking
- Ollama connection support

### Run using Docker

Make sure Docker Desktop is installed.

Start the application:

```bash
docker compose up --build
```

The services will start:

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

To stop:

```bash
docker compose down
```

### Note about Ollama

Ollama runs separately on the host machine. Make sure Ollama is running:

```bash
ollama serve
```

The Docker backend connects to Ollama running on your machine.

### Docker 支持（中文说明）

RAG-Professor 可以完全通过 Docker Compose 运行。

应用包含：
- FastAPI 后端容器
- React 前端容器
- 自动内部网络连接
- Ollama 连接支持

**使用 Docker 运行**

确保已安装 Docker Desktop，然后启动应用：
```bash
docker compose up --build
```

服务启动后：
- 前端：http://localhost:5173
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

停止服务：
```bash
docker compose down
```

**关于 Ollama 的说明**

Ollama 需要在宿主机上单独运行，请确保 Ollama 正在运行：
```bash
ollama serve
```
Docker 后端会连接到你电脑上运行的 Ollama。

---

## 2. One-time setup

### 2.1 Python
Install Python 3.10 or 3.11 (3.12+ can have wheel-availability issues with
some of these packages). Confirm with:
```
python --version
```

### 2.2 Ollama (runs the LLM)
Get it from https://ollama.com/download if you don't already have it.

Pull the models you need (one-time downloads, needs internet). At minimum:
```
ollama pull qwen3:8b
ollama pull qwen3-vl:2b
```
- The chat model (default **`qwen3:8b`**, adjust per the hardware table
  above) answers your questions — text chat, coding, math, general Q&A
  over the document.
- **`qwen3-vl:2b`** is only used automatically when a PDF page has little or
  no extractable text (i.e. it's scanned/image-only) — it OCRs that page
  before chunking. You never call it directly; ingestion decides per-page.

Then leave Ollama's server running in its own terminal window:
```
ollama serve
```
(If you installed Ollama as a Windows service, or via Homebrew/systemd on
macOS/Linux, it may already be running in the background — check with
`ollama list`.)

Verify installed models any time:
```bash
ollama list
```
Example output:
```text
NAME
qwen3:8b
qwen3:4b
gemma3:4b
```

Any installed Ollama model can be selected inside the application without
reinstalling RAG-Professor — the chat and vision models can be swapped
anytime from the sidebar dropdowns without restarting anything.

### 2.3 PyTorch (needed for embeddings; CPU build is fine and recommended)
```
pip install torch --index-url https://download.pytorch.org/whl/cpu
```
We deliberately install the **CPU** build of PyTorch here — the embedding
model runs on CPU by default (see "Why CPU embeddings?" below), so you
don't need the multi-GB CUDA build of torch at all. This alone saves you
a large, fragile install step.

If you later want GPU embeddings anyway (only worth it if your GPU has
VRAM to spare beyond what the LLM needs), replace the command above with
the CUDA build matching your driver from
https://pytorch.org/get-started/locally/, and set `EMBEDDING_DEVICE=cuda`
(see Configuration below).

### 2.4 Everything else
```
cd rag_project
pip install -r requirements.txt
```

The first time you run the app, `sentence-transformers` will download the
embedding model (`BAAI/bge-base-en-v1.5`, ~440MB) — this needs internet
**once**. After that, it's cached locally and the app works fully offline.

---

## 3. Running Without Docker / 如何运行（不使用 Docker）

Two services need to run:

### Terminal 1 — Ollama

Start Ollama:
```bash
ollama serve
```

Verify models:
```bash
ollama list
```

### Terminal 2 — Backend

From the project root:
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Terminal 3 — Frontend
```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser.

### 如何运行（中文说明）

需要同时运行三个终端：

**终端 1 — Ollama**

启动 Ollama：
```bash
ollama serve
```
查看已安装模型：
```bash
ollama list
```

**终端 2 — 后端**

在项目根目录运行：
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

**终端 3 — 前端**
```bash
cd frontend
npm install
npm run dev
```

然后在浏览器中打开 **http://localhost:5173**。

---

## 4. Using it / 如何使用

1. Drag a PDF or TXT onto the sidebar (or click to browse).
2. Wait for indexing to finish (a few seconds for a typical document —
   watch the CPU meter, that's the embedding step running).
3. Ask questions in the chat box. Answers stream in live, with clickable
   page citations under each answer.
4. Every AI answer has **Copy** (clipboard) and **Read aloud** (uses your
   browser's built-in text-to-speech, works offline) buttons.
5. Previous conversations are stored in history. Selecting a previous
   conversation restores the complete question-answer flow instead of only
   the original question.
6. Follow-up questions understand previous messages:

   Example:

   User: "What are the main points of this chapter?"

   A: "..."

   User: "Explain the second point in detail."

   The assistant uses previous conversation context automatically.
7. Uploading a new file replaces the current one (this app is designed
   for one document at a time). The original file is deleted from disk
   immediately after indexing — only the searchable index remains.

### 如何使用（中文说明）

1. 将 PDF 或 TXT 文件拖到侧边栏（或点击浏览选择文件）。
2. 等待索引完成（普通文档只需几秒钟 — 可观察 CPU 使用率，这是在进行
   向量嵌入处理）。
3. 在聊天框中提问。答案会实时流式显示，并在下方附带可点击的页码引用。
4. 每条 AI 回答都有 **复制**（Copy，复制到剪贴板）和 **朗读**
   （Read aloud，使用浏览器内置的离线文本转语音功能）按钮。
5. 之前的对话会保存在历史记录中。选择某条历史记录会恢复完整的
   问答流程，而不仅仅是原始问题。
6. 追问（后续问题）会自动理解上下文：

   示例：

   用户："这一章的主要内容是什么？"

   助手："……"

   用户："详细解释第二点。"

   助手会自动结合之前的对话上下文来回答。
7. 上传新文件会替换当前文件（本应用一次只处理一个文档）。原始文件
   在完成索引后会立即从磁盘删除，只保留可供搜索的索引数据。

---

## 5. Conversational Memory / 对话记忆

Version 1 adds conversation-aware RAG.

The system stores previous question-answer pairs and uses them when
generating new responses.

Memory features:
- Maintains conversation continuity
- Understands follow-up questions
- Restores previous conversations
- Clears memory when a new document is uploaded

Important: Conversation history is used only for context. Document
retrieval remains the source of truth for factual answers.

### 对话记忆（中文说明）

V1 版本增加了具备对话感知能力的 RAG。

系统会保存之前的问答对，并在生成新回答时加以利用。

记忆功能：
- 保持对话连续性
- 理解追问（后续问题）
- 恢复历史对话
- 上传新文档时会清空记忆

重要提示：对话历史仅用于提供上下文，文档检索结果始终是事实性
答案的最终依据。

---

## 6. Language Support / 语言支持

RAG-Professor supports both **English** and **Chinese (中文)**:
- Documents (PDF/TXT) written in English or Chinese can be ingested,
  chunked, and embedded for retrieval.
- The chat interface can be used to ask questions in either English or
  Chinese, and answers will be generated in the language of the question
  where the underlying model supports it.
- OCR fallback for scanned pages also works with Chinese-language pages,
  provided the selected vision model supports Chinese text recognition.

Note: Answer quality in Chinese depends on the chat model chosen — larger
general-purpose models (e.g. `qwen3:8b`, `qwen2.5:14b`) tend to handle
Chinese noticeably better than the smallest CPU-only models.

### 语言支持（中文说明）

RAG-Professor 同时支持 **英文** 和 **中文**：
- 支持导入、分块并嵌入英文或中文的 PDF/TXT 文档，用于检索。
- 聊天界面支持用英文或中文提问，只要所使用的模型支持，回答会以
  提问所用的语言生成。
- 扫描页面的 OCR 回退功能同样支持中文页面，前提是所选的视觉模型
  支持中文文字识别。

提示：中文回答质量取决于所选的对话模型 — 较大的通用模型
（例如 `qwen3:8b`、`qwen2.5:14b`）通常比最小的纯 CPU 模型
在中文处理上表现明显更好。

---

## 7. Design choices & why / 设计选择与原因

- **Embeddings on CPU, LLM on GPU (when a GPU is present).** VRAM is
  usually the tightest resource on a GPU-equipped machine. Running the
  embedding model on the GPU alongside the LLM means two processes
  fighting over the same VRAM budget, which is how you get VRAM overflow,
  driver fallback to shared system memory, and heat/throttling on a
  laptop chassis. CPU embedding of a single document is fast (seconds,
  not minutes), so there's little real cost to keeping it off the GPU.

- **Match the chat model to your VRAM.** An 8B model at Q4 is roughly
  5.5GB, which is a tight fit in 6GB VRAM once the context window's KV
  cache grows during a long answer — it may spill a few layers to CPU
  under load. If a model feels slow, the fastest fixes are lowering
  `LLM_NUM_CTX` (e.g. to 4096) or switching to a smaller model like
  `qwen3:4b` from the sidebar dropdown, no restart needed.

- **Vision model for OCR/vision only**, used when a PDF page comes back
  with almost no extractable text (scanned pages, photographed pages,
  image-only PDFs). Ollama loads/unloads models from VRAM as needed, so
  this doesn't have to coexist with the chat model in memory at the same
  time — it's swapped in briefly during ingestion, then swapped back out.

- **No cross-encoder reranker by default.** It's implemented and you can
  turn it on (`USE_RERANKER=true`), but for a single document with top-5
  retrieval, hybrid search (vector + BM25 fused with Reciprocal Rank
  Fusion) already gets you most of the accuracy benefit without loading
  a third model.

### 设计选择说明（中文）

- **嵌入在 CPU 上运行，大语言模型在 GPU 上运行（如果有 GPU）。**
  在配备 GPU 的机器上，显存通常是最紧张的资源。如果让嵌入模型和
  大语言模型同时争抢同一块显存，容易导致显存溢出、驱动回退到共享
  系统内存，以及笔记本发热降频等问题。单个文档的 CPU 嵌入速度很快
  （几秒钟而非几分钟），所以不用 GPU 来做嵌入几乎没有实际代价。

- **根据显存选择对话模型。** 一个 Q4 量化的 8B 模型大约占用 5.5GB，
  在 6GB 显存中会比较紧张，一旦长回答导致上下文 KV 缓存增长，
  可能会有部分层被挤到 CPU 上运行。如果模型响应变慢，最快的解决
  办法是降低 `LLM_NUM_CTX`（例如设为 4096），或在侧边栏下拉菜单中
  切换为更小的模型，如 `qwen3:4b`，无需重启。

- **视觉模型仅用于 OCR/视觉识别**，当 PDF 页面几乎没有可提取文本时
  （扫描页、拍照页、纯图片 PDF）会自动启用。Ollama 会按需加载/卸载
  显存中的模型，因此视觉模型不需要与对话模型同时常驻内存 — 它只在
  文档导入阶段短暂加载，之后会被卸载。

- **默认不启用交叉编码器重排序（reranker）。** 该功能已实现，你可以
  通过设置 `USE_RERANKER=true` 启用它，但对于单文档、Top-5 检索的场景，
  混合搜索（向量检索 + BM25，通过 Reciprocal Rank Fusion 融合）已经能
  获得大部分准确率提升，无需额外加载第三个模型。

---

## 8. Configuration / 配置说明

Everything tunable lives in `backend/config.py` with environment-variable
overrides. Set these before running, e.g. in PowerShell:
```
$env:LLM_MODEL="qwen3:4b"
```

| Variable | Default | What it does |
|---|---|---|
| `LLM_MODEL` | `qwen3:8b` | Chat model. Any model you've pulled with `ollama pull` |
| `VISION_MODEL` | `qwen3-vl:2b` | Auto-used for OCR of scanned PDF pages |
| `AUTO_OCR` | `true` | Set `false` to disable automatic OCR fallback entirely |
| `OCR_MIN_CHARS_PER_PAGE` | `40` | Below this many extracted chars, a page is treated as scanned |
| `OCR_MAX_PAGES` | `60` | Safety cap on how many pages will be OCR'd per upload |
| `EMBEDDING_DEVICE` | `cpu` | `cpu` or `cuda` |
| `EMBEDDING_MODEL` | `BAAI/bge-base-en-v1.5` | Swap for `BAAI/bge-small-en-v1.5` if you want faster/lighter |
| `USE_RERANKER` | `false` | Adds a cross-encoder rerank pass (more accurate, more compute) |
| `TOP_K` | `5` | How many chunks are sent to the LLM as context |
| `CHUNK_SIZE_TOKENS` | `700` | Target chunk size |
| `LLM_NUM_CTX` | `8192` | Context window given to Ollama |
| `MAX_FILE_SIZE_MB` | `200` | Upload size cap |

The chat and vision models can also be switched live from the two
dropdowns in the sidebar — this calls `POST /api/model` and takes effect
on your next question/upload, no restart required.

**If you want a lighter/faster setup** (e.g. running on modest hardware
or while other apps are open): `LLM_MODEL=qwen3:4b` — noticeably faster
generation, with a moderate quality trade-off.

**If you want maximum quality** and have the VRAM/RAM to spare:
`USE_RERANKER=true` plus a larger model like `qwen2.5:14b` or
`deepseek-r1:14b` — but a 14B model at Q4 is roughly 9GB, which will
**not** fit in 6GB VRAM and will run partly on CPU. Expect it to be
slower and to use significantly more RAM.

### 配置说明（中文）

所有可调参数都在 `backend/config.py` 中，也可以通过环境变量覆盖。
在运行前设置这些变量，例如在 PowerShell 中：
```
$env:LLM_MODEL="qwen3:4b"
```

上表中的变量说明：
- `LLM_MODEL`：对话模型，可以是任何通过 `ollama pull` 拉取的模型
- `VISION_MODEL`：自动用于扫描 PDF 页面的 OCR 识别
- `AUTO_OCR`：设为 `false` 可完全禁用自动 OCR 回退功能
- `OCR_MIN_CHARS_PER_PAGE`：提取字符数低于该值的页面会被视为扫描页
- `OCR_MAX_PAGES`：每次上传允许 OCR 的最大页数（安全上限）
- `EMBEDDING_DEVICE`：`cpu` 或 `cuda`
- `EMBEDDING_MODEL`：嵌入模型，如需更快/更轻量可换成 `BAAI/bge-small-en-v1.5`
- `USE_RERANKER`：启用交叉编码器重排序（更准确，但计算量更大）
- `TOP_K`：发送给大语言模型作为上下文的分块数量
- `CHUNK_SIZE_TOKENS`：目标分块大小
- `LLM_NUM_CTX`：Ollama 使用的上下文窗口大小
- `MAX_FILE_SIZE_MB`：上传文件大小上限

对话模型和视觉模型也可以直接在侧边栏的两个下拉菜单中实时切换 —
这会调用 `POST /api/model`，在下一次提问/上传时生效，无需重启。

**如果想要更轻量/更快的配置**（例如硬件较弱，或同时运行其他程序）：
设置 `LLM_MODEL=qwen3:4b` — 生成速度明显更快，质量略有下降。

**如果想要最高质量**且显存/内存充足：设置 `USE_RERANKER=true`，
并使用更大的模型如 `qwen2.5:14b` 或 `deepseek-r1:14b` — 但 14B 模型
在 Q4 量化下约占用 9GB，无法完全放入 6GB 显存，会有部分在 CPU 上
运行，速度会更慢，内存占用也会明显增加。

---

## 9. Offline Usage / 离线使用

Internet is required only for:
- Installing Ollama
- Pulling models (`ollama pull`)
- Downloading embedding models on first launch

After setup is complete, RAG-Professor can operate entirely offline.

### 离线使用（中文说明）

只有以下情况需要联网：
- 安装 Ollama
- 拉取模型（`ollama pull`）
- 首次启动时下载嵌入模型

完成设置后，RAG-Professor 可以完全离线运行。

---

## 10. Troubleshooting / 常见问题排查

- **"Cannot reach Ollama"** — make sure `ollama serve` is running and
  `ollama list` shows your model.
- **Sidebar shows GPU as "n/a"** — `nvidia-smi` isn't on your PATH, or
  drivers aren't installed. The app still works, just without live GPU
  stats; Ollama will still use the GPU internally if available.
- **First upload is slow** — the embedding model is downloading (one-time,
  needs internet). Subsequent runs are fast and fully offline.
- **Answers seem to ignore the document** — check the citation chips
  under the answer; if none appear, your question likely isn't covered
  by the document, and the model is told to say so rather than guess.
- **Everything feels sluggish** — check the RAM meter in the sidebar. If
  it's pinned near 100%, close browser tabs/other apps; the OS will be
  swapping to disk, which no amount of GPU tuning fixes.
- **Upload fails with "No extractable text found"** — either the file is
  genuinely empty, or (for a scanned PDF) OCR failed. Check the terminal
  log for `OCR'd page N with <vision model>` lines; if you don't see them,
  make sure the vision model is pulled (`ollama list`) and `AUTO_OCR` isn't
  set to `false`.
- **Chat box stays greyed out / nothing is clickable** — this almost
  always means the upload itself failed silently. Check the terminal
  running `uvicorn` for the actual error; every error is returned as
  JSON with a real message instead of a generic crash, so the popup
  alert on upload should tell you what went wrong.
- **You see `Failed to send telemetry event ... capture()` in the logs**
  — this is ChromaDB's anonymous usage telemetry hitting a bug in its own
  library, not a problem with your data. It's disabled in this build; if
  you still see it, make sure you're running the latest files.

### 常见问题排查（中文说明）

- **“无法连接到 Ollama”** — 确认 `ollama serve` 正在运行，并且
  `ollama list` 中能看到你的模型。
- **侧边栏 GPU 显示为 “n/a”** — 说明 `nvidia-smi` 不在系统 PATH 中，
  或者显卡驱动未安装。应用依然可以正常工作，只是无法显示实时 GPU
  状态；如果有可用显卡，Ollama 内部仍会使用它。
- **首次上传较慢** — 是因为正在下载嵌入模型（仅首次需要联网），
  之后的运行会很快，且完全离线。
- **回答似乎没有参考文档内容** — 检查回答下方的引用标签；如果没有
  引用出现，说明你的问题很可能没有在文档中被覆盖，模型被要求如实
  说明而不是随意猜测。
- **整体运行卡顿** — 查看侧边栏的内存使用率，如果接近 100%，请关闭
  浏览器标签页或其他程序；否则系统会开始使用磁盘交换空间，这是任何
  GPU 调优都无法解决的。
- **上传失败并提示“未找到可提取文本”** — 要么文件本身是空的，要么
  （对于扫描版 PDF）OCR 失败了。查看终端日志中是否有
  `OCR'd page N with <vision model>` 这样的记录；如果没有，请确认已
  拉取视觉模型（`ollama list`）且 `AUTO_OCR` 未被设为 `false`。
- **聊天框保持灰色 / 无法点击** — 几乎都是因为上传本身静默失败了。
  查看运行 `uvicorn` 的终端窗口获取真实错误信息；每个错误都会以
  JSON 格式返回真实的错误信息，而不是笼统的崩溃提示，因此上传时的
  弹窗提示应该会告诉你具体哪里出了问题。
- **日志中出现 `Failed to send telemetry event ... capture()`** —
  这是 ChromaDB 匿名使用统计功能本身的一个小 bug，与你的数据无关。
  该功能在本构建中已被禁用；如果仍然看到，请确认你运行的是最新文件。

---

## 11. Installing Additional Models / 安装更多模型

RAG-Professor uses Ollama, which makes switching models easy.

```bash
ollama pull qwen3:8b
```
or
```bash
ollama pull qwen3:4b
```
or
```bash
ollama pull gemma3:4b
```

Verify installed models:
```bash
ollama list
```

Any installed Ollama model can be selected inside the application without
reinstalling RAG-Professor.

### 安装更多模型（中文说明）

RAG-Professor 使用 Ollama，切换模型非常方便。

```bash
ollama pull qwen3:8b
```
或
```bash
ollama pull qwen3:4b
```
或
```bash
ollama pull gemma3:4b
```

查看已安装的模型：
```bash
ollama list
```

任何已安装的 Ollama 模型都可以直接在应用内选择使用，无需重新安装
RAG-Professor。

---

## 12. Project structure / 项目结构

```
rag_project/
├── backend/
│   ├── main.py              FastAPI API and routes
│   ├── config.py            Application configuration
│   ├── ingestion.py         PDF/TXT processing and chunking
│   ├── embeddings.py        Embedding generation
│   ├── vectorstore.py       ChromaDB + BM25 hybrid retrieval
│   ├── llm.py               Ollama streaming client
│   ├── rag_engine.py        RAG pipeline and conversation context
│   ├── runtime_state.py     Conversation memory management
│   └── system_monitor.py    CPU/RAM/GPU monitoring
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   └── HistoryPanel.jsx
│   │   └── ...
│
├── docker-compose.yml
├── backend/Dockerfile
├── frontend/Dockerfile
├── requirements.txt
├── .gitignore
└── README.md
```
