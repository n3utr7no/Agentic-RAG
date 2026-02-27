from config.llms import light_model
from core.models import AnswerRelevance
from config.prompts import GRADER_PROMPT


def router_node(query: str, answer: str):
    """Returns a boolean (True or False) regarding whether the answer generated is relevant to the user query or not."""
    print('----Routing answer----')
    result = light_model.with_structured_output(AnswerRelevance).invoke(GRADER_PROMPT.format(query=query, answer=answer))
    return result
