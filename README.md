# FolderMind

**Local-first, permission-aware document Q&A for manufacturing teams.**

FolderMind is a retrieval-augmented generation (RAG) prototype that lets users ask natural-language questions about indexed files and receive answers grounded in retrieved document passages. Before retrieval, the backend restricts ChromaDB search results using directory metadata and a user's configured access grants. Answer generation runs locally through Ollama.

The current demo uses **fictional manufacturing data** across Production, Quality, and HR folders. It includes a lightweight browser-based chat UI and FastAPI backend.

> [!IMPORTANT]
> **Project status: working local prototype, not production-ready security software.** Access grants are hardcoded test fixtures; the web API currently runs as the fixed demo user `alex`. There is no user authentication, security audit, or enterprise permission synchronization. Do not index real confidential employee or company records in this version.

## Demo capabilities

- **Local document Q&A:** Ask about work orders, inspection notes, and other indexed text records.
- **Directory-filtered retrieval:** ChromaDB's metadata `where` filter limits which chunks may be retrieved *before* they reach the LLM.
- **Persistent vector store:** ChromaDB persists indexed chunks, embeddings, and metadata across runs.
- **Source-aware responses:** Retrieved passages are labeled `[Source 1]`, `[Source 2]`, etc.; generated citations are checked for valid source numbers and resolved to source files in backend logs.
- **Citation retry:** If an answer lacks a valid citation, the backend retries once with stricter formatting instructions. It reports a failure if the second response still lacks valid references.
- **Local generation:** Ollama serves the `llama3.2:latest` model without requiring a cloud LLM API.
- **Web demo:** A plain HTML/CSS/JavaScript chat interface sends questions to FastAPI's `POST /ask` endpoint.

**Currently supported indexing format:** `.txt`. PDF, Word, Excel, and CSV ingestion are planned, **not yet implemented**. The web interface displays citation labels in answer text, but does not yet render a clickable source panel.

## Architecture

```text
                          INDEXING (run separately)
  demo_data/{production,quality,hr}/*.txt
                     |
              scanner.py
                     |
       text extraction + chunking.py
        (500 characters, 100 overlap)
                     |
     IDs + source/directory metadata
                     |
         ChromaDB persistent store
      (embeddings + text + metadata)

                          QUESTION ANSWERING
  Browser UI (static/index.html)
                     |
             POST /ask (JSON)
                     |
              FastAPI (api.py)
                     |
                ask.py
                     |
       Demo identity + permissions.py
                     |
        retrieval.py: ChromaDB query
      filtered by authorized directories
                     |
         Source-labeled evidence
                     |
       generation.py: local Ollama
                     |
     citations.py: validate / resolve
                     |
           JSON answer to browser
```

**Why RAG?** Rather than sending an entire manual or document archive to an LLM, FolderMind chunks documents, embeds them, and retrieves a small set of relevant passages for each question. This reduces unnecessary context and makes source tracing possible. Retrieval returns *candidates*, not guaranteed answers; semantic similarity alone does not establish factual support.

### How the permission filter works

The indexer stores a record with each chunk, for example:

```python
{
    "source": "hr/employees.txt",
    "directory": "hr",
    "chunk_index": 0,
}
```

The demo permissions are defined in `src/foldermind/permissions.py`:

| Demo user | Permitted directories |
| --- | --- |
| `alex` | Production |
| `maya` | Production, Quality |
| `sam` | HR |
| Unknown username | None (deny by default) |

Retrieval determines the user's grants first, then submits a query similar to:

```python
collection.query(
    query_texts=[question],
    n_results=3,
    where={"directory": {"$in": sorted(allowed)}},
)
```

This is a **retrieval-level access-control demonstration**, not an authentication system. The currently exposed `/ask` endpoint uses **`alex` for every browser request**; it does not allow signing in as Maya or Sam. The demo permissions can be exercised programmatically or in tests.

## Tech stack

| Layer | Technology |
| --- | --- |
| Language | Python 3.13 (current development environment) |
| API | FastAPI + Uvicorn + Pydantic |
| Web UI | HTML, CSS, vanilla JavaScript |
| Chunking | LangChain `RecursiveCharacterTextSplitter` |
| Embeddings and vector search | ChromaDB default embedding function / persistent collection |
| Local LLM | Ollama with `llama3.2:latest` |
| Testing | pytest |

## Run locally

**Prerequisites:** Python 3.13, Git, and [Ollama](https://ollama.com/) installed. Run the commands below from the repository root. Use only the provided fictional demo data.

### 1. Clone and install

```bash
git clone https://github.com/harshanb07/folderMind.git
cd folderMind
```

**Windows PowerShell:**

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**macOS / Linux:**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

The pinned `requirements.txt` was generated from a Windows development environment. Some transitive pins may need adjustment on another operating system; cross-platform installation has not been fully verified.

### 2. Start Ollama and obtain the model

```bash
ollama pull llama3.2:latest
ollama list
```

Make sure the Ollama service is running (the Ollama desktop application normally starts it, or use `ollama serve` if necessary).

### 3. Index the fictional documents

**Windows:**

```powershell
.\.venv\Scripts\python.exe src\foldermind\indexer.py
```

**macOS / Linux:**

```bash
.venv/bin/python src/foldermind/indexer.py
```

The current sample data produces **six chunks** (two each from Production, Quality, and HR). The collection is persisted in `./chroma_db/`, which is excluded from Git.

### 4. Launch the web application

**Windows:**

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.foldermind.api:app --reload
```

**macOS / Linux:**

```bash
.venv/bin/python -m uvicorn src.foldermind.api:app --reload
```

Open **http://127.0.0.1:8000/** for the chat interface, or **http://127.0.0.1:8000/docs** for interactive API documentation. The default API binding is local to your machine.

### Example questions

With the **browser demo user Alex (Production)**:

| Question | Expected behavior |
| --- | --- |
| `What is the status of WO-9001?` | Answers **In Progress**, citing a Production passage |
| `How many units remain on WO-9001?` | Answers **45 units**, if the correct passage is retrieved and cited |
| `Why is WO-9002 on hold?` | Answers **Fixture alignment issue**, if supported by retrieved evidence |
| `What is Jordan Ellis's salary?` | Should not reveal the HR-only salary; may currently produce a citation-format error instead of a clean abstention |

To test the HR case without changing the web API, use the existing Python demo/test code with `sam` (HR grant). These records are entirely fictional.

### Run tests

**Windows:**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_citations.py tests/test_retrieval.py -v
```

**macOS / Linux:**

```bash
.venv/bin/python -m pytest tests/test_citations.py tests/test_retrieval.py -v
```

`test_retrieval.py` uses the local indexed ChromaDB collection, so **run the indexer before these tests**. Tests for independent, temporary collections are a future improvement. Empty placeholder test modules also exist in the repository.

## Repository layout

```text
folderMind/
├── demo_data/                 # Fictional Production, Quality, HR records
├── src/foldermind/
│   ├── scanner.py             # Discover .txt files recursively
│   ├── chunking.py            # Split text into overlapping passages
│   ├── indexer.py             # Upsert records into ChromaDB
│   ├── permissions.py         # Demo user-to-directory grants
│   ├── retrieval.py           # Permission-filtered vector search
│   ├── generation.py          # Ollama interaction and prompting
│   ├── citations.py           # Citation syntax checks and source lookup
│   ├── ask.py                 # End-to-end RAG orchestration
│   └── api.py                 # FastAPI routes and frontend serving
├── static/index.html          # Browser chat demo
├── tests/                     # Citation and retrieval checks
└── requirements.txt
```

## Engineering challenges and lessons learned

### 1. Good retrieval does not guarantee a good answer

An early test asked: **“What caused the machine stoppage on WO-7312?”** The top retrieved passage documented a **35-minute stoppage due to a tool-change alarm**, but the LLM initially hedged and said the cause was not established. The underlying *motor failure* cause was not documented; the triggering *alarm event* was.

To isolate the failure, I tested generation with the source text directly, without ChromaDB, and refined the prompt to distinguish a documented event from an unknown root cause. This demonstrated that **retrieval quality and answer generation quality must be debugged separately**.

### 2. Valid evidence can still produce a missing citation

The model sometimes answered an HR salary question correctly but omitted `[Source 1]`. `validate_citations()` rejected the answer, despite the relevant HR passage being retrieved. I added a **single retry** with explicit citation-format instructions. This improved the result in the local demo:

```text
First attempt:  Jordan Ellis's annual salary is $72,000 CAD.
Retry:          According to [Source 1], Jordan Ellis's annual salary is $72,000 CAD.
Resolved:       hr/employees.txt, chunk 0
```

Citation validation currently checks **whether reference numbers are present and in range**, not whether each cited passage truly supports every claim. The exact-string abstention check is also fragile and can produce an unhelpful citation error for questions whose answers are unavailable.

### 3. Indexing and retrieval are different phases

The indexer finds files, splits text into chunks, adds unique IDs and metadata, and upserts them into a persistent collection. A user query does **not** reindex all documents: ChromaDB embeds the question and searches the existing collection, subject to an authorization filter. `upsert()` updates existing IDs but the current indexer does **not** remove obsolete chunk IDs when files shrink or are deleted.

## Current limitations and roadmap

- [ ] **Authentication and authorization hardening:** Replace hardcoded usernames with authenticated identities and configurable access rules; validate paths and symlinks, and test for leakage before processing real records.
- [ ] **Structured answer responses:** Return explicit `answered`, `insufficient_evidence`, or `citation_error` statuses, with source metadata; render clickable citations in the frontend.
- [ ] **Expanded file loaders:** PDF (`.pdf`), Word (`.docx`), spreadsheet (`.xlsx`), CSV (`.csv`) and Markdown (`.md`), preserving page/sheet/row provenance.
- [ ] **Reliable indexing:** Handle deleted files, stale chunks, updates, unsupported files, and malformed documents.
- [ ] **Retrieval quality:** Add relevance thresholds/evaluation cases so the nearest chunks aren't mistaken for evidence that answers the question.
- [ ] **Test isolation:** Build temporary ChromaDB fixtures and more end-to-end, permission-denial, citation and prompt-injection tests.
- [ ] **Packaging:** Add Docker Compose and reproducible, cross-platform dependency setup; keep Ollama local where appropriate.
- [ ] **Operator documentation:** Clarify configuration, logs, backup/restore, resource requirements and security boundaries.

## Privacy and security

FolderMind is designed as a **local-first prototype**: document indexing, vector storage, and answer generation run on the user's machine. This does **not** automatically make it secure. The current demo has no login, the browser always operates as Alex, the directory grants are hardcoded, and citation checks are not full factual verification. Keep it bound to localhost and use fictional or non-sensitive documents only.

## Project intent

FolderMind explores how local language models, vector search, and explicit directory permissions can help manufacturing teams find information across production records, inspection documentation, and internal procedures—without requiring a cloud LLM for every question.

*Built as an iterative AI engineering project: ship a working pipeline, test it, investigate failures, then harden it.*
