from typing import Literal
from src.agents.keywords_agent.state import KeywordState

async def route_to_query_or_analysis(state: KeywordState) -> Literal["query_generator", "competitor_analysis"]:
    """
    Takes the tool response from the "tools" node and determines using LLM whether to route to the "query_generator" or "competitor_analysis" node.
    If tool response contains sufficient competitor information, it will route to the "competitor_analysis" node.
    If tool response is not sufficient, it will route to the "query_generator" node to generate new search queries.
    
    Updates:
        - state._web_search_results_accumulated: updates it with the tool response. Adds the search queries to the tool response as well.
    """
    return state["route_to"]