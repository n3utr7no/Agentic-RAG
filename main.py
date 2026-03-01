from pydantic_ai import Agent, ModelSettings, RunContext
from tools import search_node, retrieve_node, router_node
from config.prompts import SYSTEM_PROMPT
from core.models import AgentState
from dotenv import load_dotenv

load_dotenv()

agent = Agent(
    'gateway/groq:llama-3.3-70b-versatile',
    deps_type=AgentState,
    system_prompt=SYSTEM_PROMPT,
    retries=2,
)

@agent.tool
def research(ctx: RunContext[AgentState], query: str, use_knowledge_base: bool = True) -> str:
    """Performs research for a query. Set use_knowledge_base to True for topics in the knowledge base (LLM security, agent patterns, RAG), or False for general queries (current events, general knowledge)."""

    if use_knowledge_base:
        # Full RAG pipeline: retrieve + search + grade
        docs = retrieve_node(query)
        ctx.deps.documents.extend(docs)

        web_results = search_node(query)
        ctx.deps.documents.extend(web_results)

        all_context = docs + web_results
        combined = "\n\n".join(all_context) if all_context else ""

        relevance = router_node(query=query, answer=combined)
        if relevance.is_not_relevant:
            extra_results = search_node(query)
            ctx.deps.documents.extend(extra_results)
            all_context.extend(extra_results)
            combined = "\n\n".join(all_context)

        return combined if combined else "No relevant information found."
    else:
        # Web-only search
        print('----Web searching----')
        results = search_node(query)
        ctx.deps.documents.extend(results)
        return "\n\n".join(results) if results else "No results found."

if __name__ == "__main__":
    current_state = AgentState(documents=[])
    result = agent.run_sync("What are good agent patterns?", deps=current_state, model_settings=ModelSettings(temperature=0.0))
    print(result.output)
