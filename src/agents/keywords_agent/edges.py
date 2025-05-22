from typing import Literal
from src.agents.keywords_agent.state import KeywordState
from src.agents.keywords_agent.schemas import RouteToQueryOrAnalysis
from src.utils.models_initializer import get_gemini_model, get_groq_model, initialize_model_with_fallbacks


# define router model with fallbacks and structured output.
ROUTER_MODEL_WITH_FALLBACK_AND_STRUCTURED = initialize_model_with_fallbacks(
    primary_model_fn=get_gemini_model,
    primary_model_kwargs={"model_name": 2, "temperature": 0.2},
    fallback_model_fns=[get_groq_model, get_gemini_model],
    fallback_model_kwargs_list=[
        {"model_name": 1, "temperature": 0.2},
        {"model_name": 3, "temperature": 0.2}
    ],
    structured_output_schema=RouteToQueryOrAnalysis,
)

async def route_to_query_or_analysis(state: KeywordState) -> Literal["query_generator", "competitor_analysis"]:
    """
    Takes the tool response from the "tools" node and determines using LLM whether to route to the "query_generator" or "competitor_analysis" node.
    If tool response contains sufficient competitor information, it will route to the "competitor_analysis" node.
    If tool response is not sufficient, it will route to the "query_generator" node to generate new search queries.
    
    Updates:
        - state._web_search_results_accumulated: updates it with the tool response. Adds the search queries to the tool response as well.
    """
    if state["tool_call_count"] >= 2:
        # if we have already called the tool twice, we will not call it again
        return "competitor_analysis"
    else:
        # Get the tool response from the most recent message
        tool_response = state["messages"][-1].content
        
        # Get the search queries from the state
        search_queries: list[str] = state.get("generated_search_queries", [])
        
        # get user input and entities as well
        user_input: str = state.get("user_input", "")
        retrieved_entities: list[str] = state.get("retrieved_entities", [])

        print(f"\n*****Tool call count:{state['tool_call_count']}\n")

        # for now lets just return "competitor_analysis" to test the flow
        return "competitor_analysis"