from pydantic_ai import Agent, ModelSettings, RunContext
from tools import search_node, retrieve_node, router_node
from config.prompts import SYSTEM_PROMPT
from core.models import AgentState
from dotenv import load_dotenv

load_dotenv()

agent = Agent(
    'gateway/groq:llama-3.3-70b-versatile',
    deps_type=AgentState,
    system_prompt=SYSTEM_PROMPT
)

@agent.tool
def research(ctx: RunContext[AgentState], query: str) -> str:
    """Performs full RAG research: retrieves local docs, searches the web, grades the combined result, and re-searches if needed."""

    # 1. Retrieve from local vector store
    docs = retrieve_node(query)
    ctx.deps.documents.extend(docs)

    # 2. Search the web
    web_results = search_node(query)
    ctx.deps.documents.extend(web_results)

    # 3. Combine context
    all_context = docs + web_results
    combined = "\n\n".join(all_context) if all_context else ""

    # 4. Grade — if not good enough, do another round of web search
    relevance = router_node(query=query, answer=combined)
    if relevance.is_not_relevant:
        extra_results = search_node(query)
        ctx.deps.documents.extend(extra_results)
        all_context.extend(extra_results)
        combined = "\n\n".join(all_context)

    return combined if combined else "No relevant information found."

if __name__ == "__main__":
    current_state = AgentState(documents=[])
    result = agent.run_sync("What are good agent patterns?", deps=current_state, model_settings=ModelSettings(temperature=0.0))
    print(result.output)
