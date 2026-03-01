from pydantic import BaseModel, Field, ConfigDict
from typing import List

class AgentState(BaseModel):
    documents : List[str] = Field(description='The list of texts of the relevant context')

class Queries(BaseModel):
    queries: List[str] = Field(description='List of search queries, max 3.')

class AnswerRelevance(BaseModel):
    model_config = ConfigDict(extra='ignore')
    is_not_relevant : bool = Field(description='Is search required to answer the users query or not. True if it is required and False if not.')
