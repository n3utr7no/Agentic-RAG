import streamlit as st
import os
import sys
import io
import contextlib
from pathlib import Path
from dotenv import load_dotenv

# Ensure local imports resolve
RAG_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(RAG_ROOT))
load_dotenv(RAG_ROOT / ".env")

st.set_page_config(page_title="Agentic RAG", page_icon="🔍", layout="centered")

# ── CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.header-container { text-align: center; padding: 1.5rem 0 1rem; }
.header-container h1 {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.4rem; font-weight: 700; margin-bottom: 0.2rem;
}
.header-container p { color: #999; font-size: 1rem; margin-top: 0; }

div[data-testid="stStatusWidget"] {
    border: 1px solid rgba(102, 126, 234, 0.2);
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("#### 🔑 Bring Your Own Keys")

    groq_key = st.text_input("Groq API Key", type="password", value=os.getenv("GROQ_API_KEY", ""))
    tavily_key = st.text_input("Tavily API Key", type="password", value=os.getenv("TAVILY_API_KEY", ""))
    gateway_key = st.text_input("Gateway Key", type="password", value=os.getenv("PYDANTIC_AI_GATEWAY_API_KEY", ""))

    keys_ready = bool(groq_key and tavily_key and gateway_key)
    if keys_ready:
        st.success("Keys configured", icon="✅")
    else:
        st.warning("Provide all keys to start", icon="⚠️")

    st.divider()
    st.link_button("⭐  View on GitHub", "https://github.com/n3utr7no/Agentic-RAG", use_container_width=True)

    with st.expander("📖 About"):
        st.markdown("""
**Agentic RAG** — Autonomous research agent with:
- 📚 Local vector retrieval (LanceDB)
- 🌐 Live web search (Tavily)
- 📊 LLM self-grading & auto re-search
        """)

    st.divider()
    if st.button("🗑️  Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Set env vars before any module imports
if groq_key:
    os.environ["GROQ_API_KEY"] = groq_key
if tavily_key:
    os.environ["TAVILY_API_KEY"] = tavily_key
if gateway_key:
    os.environ["PYDANTIC_AI_GATEWAY_API_KEY"] = gateway_key

# ── Header ───────────────────────────────────────────────────
st.markdown("""
<div class="header-container">
    <h1>🔍 Agentic RAG</h1>
    <p>Autonomous Research Agent with Self-Grading</p>
</div>
""", unsafe_allow_html=True)

# ── Chat ─────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Stage labels for the print() output from existing tool functions
STAGE_MAP = {
    "Retrieving docs from database": "📚 Retrieving from knowledge base...",
    "Retrieved docs from database": "📚 Retrieved relevant chunks ✅",
    "Searching node": "🔎 Generating search queries...",
    "Searching": "🌐 Searching the web...",
    "Web searching": "🌐 Web search (no knowledge base)...",
    "Routing answer": "📊 Grading answer quality...",
}

if prompt := st.chat_input("Ask about LLM security, agent patterns, RAG systems..."):
    if not keys_ready:
        st.error("⚠️ Provide all API keys in the sidebar first.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Lazy import — only triggers after env vars are set
        from main import agent
        from core.models import AgentState
        from pydantic_ai import ModelSettings

        with st.status("🔍 Researching...", expanded=True) as status:
            # Capture print() output from existing tool functions as stage indicators
            captured = io.StringIO()
            with contextlib.redirect_stdout(captured):
                result = agent.run_sync(
                    prompt,
                    deps=AgentState(documents=[]),
                    model_settings=ModelSettings(temperature=0.0),
                )

            # Display captured stages
            seen = set()
            for line in captured.getvalue().splitlines():
                clean = line.strip().strip("-").strip()
                for key, label in STAGE_MAP.items():
                    if key in clean and label not in seen:
                        st.write(label)
                        seen.add(label)
                        break

            status.update(label="✅ Research complete!", state="complete", expanded=False)

        st.markdown(result.output)
        st.session_state.messages.append({"role": "assistant", "content": result.output})
