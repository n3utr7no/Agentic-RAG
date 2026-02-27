import os
from pathlib import Path
import lancedb
from langchain_community.vectorstores import LanceDB
from langchain_text_splitters import SpacyTextSplitter
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en")

RAG_ROOT = Path(__file__).resolve().parent.parent
db_path = str(RAG_ROOT / "lancedb_data")
table_name = "rag_docs"

# SOURCES = [
#     # Original knowledge base
#     {
#         "url": "https://www.anthropic.com/engineering/building-effective-agents",
#         "type": "logic",
#         "loader": "web",
#     },
#     # Security Reports -> type: policy (used by Grader to block unsafe tool calls)
#     {
#         "url": "https://owasp.org/www-project-top-10-for-large-language-model-applications/",
#         "type": "policy",
#         "loader": "web",
#     },
#     # Technical Papers -> type: logic (used by Planner to decide retrieval strategies)
#     {
#         "url": "https://aclanthology.org/2025.findings-acl.349.pdf",
#         "type": "logic",
#         "loader": "pdf",
#     },
#     {
#         "url": "https://arxiv.org/pdf/2512.23959",
#         "type": "logic",
#         "loader": "pdf",
#     },
#     {
#         "url": "https://arxiv.org/pdf/2512.17220",
#         "type": "logic",
#         "loader": "pdf",
#     },
# ]
#
# # Load and tag documents
# all_docs = []
# for source in SOURCES:
#     print(f"Loading: {source['url']} ...")
#     try:
#         if source["loader"] == "web":
#             loader = WebBaseLoader(source["url"])
#         else:
#             loader = PyPDFLoader(source["url"])
#
#         docs = loader.load()
#         for doc in docs:
#             doc.metadata["type"] = source["type"]
#         all_docs.extend(docs)
#         print(f"  Loaded {len(docs)} page(s)")
#     except Exception as e:
#         print(f"  FAILED: {e}")
#
# # Split using SpacyTextSplitter (sentence-aware, never cuts mid-sentence)
# splitter = SpacyTextSplitter(chunk_size=512, chunk_overlap=20, pipeline="en_core_web_sm")
# split_docs = splitter.split_documents(all_docs)
# print(f"\nTotal chunks after splitting: {len(split_docs)}")
#
# # Drop old table and re-ingest
# db_conn = lancedb.connect(db_path)
# if table_name in db_conn.table_names():
#     db_conn.drop_table(table_name)
#
# vector_store = LanceDB.from_documents(
#     split_docs,
#     embedding=embedding_model,
#     connection=db_conn,
#     table_name=table_name,
# )
#
# print(f"Successfully ingested {len(split_docs)} chunks into '{table_name}'.")

# ============================================================
# Vector Store Connection (always active, for querying)
# ============================================================
db_conn = lancedb.connect(db_path)
vector_store = LanceDB(
    embedding=embedding_model,
    connection=db_conn,
    table_name=table_name,
)
