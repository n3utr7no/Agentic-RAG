from ingestion.ingest import vector_store


def retrieve_node(query: str, k: int = 5):
    """Retrieves top k docs related to the query from the database."""
    print('----Retrieving docs from database----')
    results = vector_store.similarity_search(query, k=k)
    filtered_results = [result.page_content for result in results]
    print('----Retrieved docs from database----')
    return filtered_results
