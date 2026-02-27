# 🔍 Agentic RAG

An autonomous research agent powered by **Pydantic AI** that combines local knowledge retrieval with live web search, using self-grading to ensure response quality. Built for extensibility, with a structured metadata-tagged knowledge base.

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                           User Query                             │
└──────────────────────┬───────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Pydantic AI Agent                             │
│              (LLaMA 3.3 70B via Groq)                           │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Knowledge Base Overview (in system prompt)                │  │
│  │  → Decides: call research tool OR answer directly          │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────┬───────────────────────────────────────────┘
                       │ (only if query is DB-relevant)
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                    research() Tool                               │
│                                                                  │
│  1. retrieve_node()  →  LanceDB similarity search               │
│  2. search_node()    →  Tavily web search                       │
│  3. router_node()    →  LLM-based answer grading                │
│  4. (if grading fails) → Re-search and append                   │
└──────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
rag/
├── main.py                  # Agent definition & entry point
├── config/
│   ├── llms.py              # LLM client initialization (Groq)
│   └── prompts.py           # System, grader, and search prompts
├── core/
│   └── models.py            # Pydantic schemas (AgentState, Queries, AnswerRelevance)
├── ingestion/
│   └── ingest.py            # Document loading, splitting, and vector store setup
├── tools/
│   ├── retrieval.py         # Local vector store retrieval
│   ├── search.py            # Web search via Tavily
│   └── grading.py           # LLM-based answer quality grading
└── lancedb_data/            # Persisted vector database
```

## How It Works

1. **Query Classification** — The system prompt includes a high-level overview of the knowledge base contents, allowing the LLM to decide whether to invoke the `research` tool or answer directly.

2. **Document Retrieval** — Queries the LanceDB vector store using `BAAI/bge-small-en` embeddings to find the top-k most relevant chunks.

3. **Web Search** — Generates up to 3 refined search queries using a lightweight LLM, then executes them via Tavily to retrieve supplementary context.

4. **Self-Grading** — An LLM-based grader evaluates whether the combined context sufficiently answers the query. If not, an additional search round is triggered.

## Knowledge Base

Documents are ingested with **metadata tags** for structured retrieval:

| Document Type | Tag | Purpose |
|---|---|---|
| Security Reports (OWASP) | `type: policy` | Used by the grader to assess safety-critical queries |
| Technical Papers & Guides | `type: logic` | Used for agent design and retrieval strategy decisions |

**Current sources (626 chunks):**
- [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) — Anthropic
- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [ACL 2025 Findings](https://aclanthology.org/2025.findings-acl.349.pdf)
- [arXiv:2512.23959](https://arxiv.org/pdf/2512.23959)
- [arXiv:2512.17220](https://arxiv.org/pdf/2512.17220)

**Text splitting:** SpacyTextSplitter (`en_core_web_sm`) for sentence-aware chunking — never cuts mid-sentence.

## Setup

### Prerequisites
- Python 3.11+
- API keys for Groq, Tavily, and HuggingFace

### Installation

```bash
git clone https://github.com/n3utr7no/Agentic-RAG.git
cd Agentic-RAG

python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

pip install pydantic-ai langchain-community langchain-groq langchain-huggingface \
            langchain-text-splitters sentence-transformers lancedb tavily-python \
            python-dotenv spacy pypdf

python -m spacy download en_core_web_sm
```

### Environment Variables

Create a `.env` file in the `rag/` directory:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
HUGGINGFACEHUB_API_TOKEN=your_hf_token
PYDANTIC_AI_GATEWAY_API_KEY=your_gateway_key
```

### Ingestion

To ingest documents, uncomment the `SOURCES` block in `ingestion/ingest.py` and run:

```bash
cd rag
python ingestion/ingest.py
```

After successful ingestion, comment the block back out to prevent re-ingestion on every import.

### Run

```bash
cd rag
python main.py
```

## Tech Stack

| Component | Technology |
|---|---|
| Agent Framework | [Pydantic AI](https://ai.pydantic.dev/) |
| LLM (Agent) | LLaMA 3.3 70B via Groq |
| LLM (Grader/Planner) | GPT-OSS 20B via Groq |
| Embeddings | BAAI/bge-small-en |
| Vector Store | LanceDB |
| Web Search | Tavily |
| Text Splitting | spaCy (en_core_web_sm) |
| Data Validation | Pydantic |

## Future Extensibility

### 🗄️ Query Cache Layer

Add a semantic cache to avoid redundant retrieval and LLM calls for similar queries:

```
User Query → Cache Lookup → HIT: return cached answer
                           → MISS: research() → cache result → return
```

**Planned approach:**
- Embed incoming queries and check cosine similarity against a cache index
- Cache entries include: query embedding, retrieved context, final answer, TTL
- Configurable similarity threshold (e.g., 0.95) to control cache hit sensitivity
- LanceDB itself can serve as the cache store, using a separate `cache` table
- TTL-based eviction to keep cached answers fresh

**Benefits:** Reduces Groq API calls, Tavily usage, and embedding computation for repeated or near-duplicate queries.

---

### 🛡️ Aegis Integration

[Aegis](https://github.com/n3utr7no/aegis) is a modular LLM security framework with four core modules that can be integrated into the RAG pipeline:

| Aegis Module | Integration Point | Purpose |
|---|---|---|
| **Shield** | Pre-retrieval | Scans incoming queries for prompt injection, jailbreaks, and adversarial inputs before they reach the agent |
| **Forge** | Ingestion pipeline | Validates and sanitizes documents during ingestion to prevent data poisoning |
| **Oracle** | Post-retrieval | Evaluates retrieved context for hallucination risk and factual consistency |
| **Lens** | Response output | Scans the agent's final response for data leakage, PII exposure, and unsafe content |

**Planned integration architecture:**

```
User Query
    │
    ▼
┌─────────────┐
│ Aegis Shield │ ← Prompt injection detection
└──────┬──────┘
       ▼
┌─────────────┐
│   Agent      │ → research() tool
└──────┬──────┘
       ▼
┌─────────────┐
│ Aegis Oracle │ ← Hallucination & consistency check
└──────┬──────┘
       ▼
┌─────────────┐
│ Aegis Lens   │ ← Output safety scan
└──────┬──────┘
       ▼
   Safe Response
```

This pairs naturally with the existing `type: policy` metadata — OWASP-tagged chunks can inform Shield's threat detection, while Oracle can cross-reference `type: logic` documents to verify factual claims.

## License

MIT
