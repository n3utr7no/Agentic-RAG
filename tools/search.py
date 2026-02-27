from config.llms import light_model
from core.models import Queries
from config.prompts import SEARCH_PROMPT
from tavily import TavilyClient

client = TavilyClient()


def search_node(query: str):
    """Generates queries and executes search. Returns new docs."""
    print('----Searching node----')
    queries_obj = light_model.with_structured_output(Queries).invoke(SEARCH_PROMPT.format(query=query))
    new_docs = search(queries_obj, max_results=2)
    return new_docs


def search(queries: Queries, max_results=5):
    """Uses Tavily to search for queries."""
    print('----Searching----')
    all_results = [res['content'] for query in queries.search_queries for res in client.search(query, max_results=max_results)['results']]

    return all_results
