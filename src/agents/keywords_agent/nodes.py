"""
Write all the node functions for the keywords agent here.
"""

from pprint import pprint
from typing import Any
from src.agents.keywords_agent.state import KeywordState
from langchain_core.messages import HumanMessage

# Entity Extractor related imports
from src.utils.models_initializer import initialize_model_with_fallbacks, get_gemini_model, get_groq_model
from src.agents.keywords_agent.prompts import (
    ENTITY_EXTRACTOR_PROMPT,
    QUERY_GENERATOR_PROMPT
)
from src.agents.keywords_agent.schemas import Entities
from src.tools.web_search_tool import WebSearch, dummy_web_search_tool


# #################
# Entity Extractor Model
# #################
ENTITIES_MODEL_WITH_FALLBACK_AND_STRUCTURED = initialize_model_with_fallbacks(
    primary_model_fn=get_gemini_model,
    primary_model_kwargs={"model_name": 2, "temperature": 0.5},
    fallback_model_fns=[get_groq_model, get_gemini_model],
    fallback_model_kwargs_list=[
        {"model_name": 1, "temperature": 0.5},
        {"model_name": 3, "temperature": 0.2}
    ],
    structured_output_schema=Entities,
)

# #################
# Query Generator Model
# #################'
# QUERY_GENERATOR_MODEL_WITH_FALLBACK_AND_TOOLS = initialize_model_with_fallbacks(
#     primary_model_fn=get_gemini_model,
#     primary_model_kwargs={"model_name": 1, "temperature": 0.7},
#     fallback_model_fns=[get_groq_model, get_gemini_model],
#     fallback_model_kwargs_list=[
#         {"model_name": 2, "temperature": 0.7},
#         {"model_name": 2, "temperature": 0.7}
#     ],
#     bind_tools=True,
#     # tools=[WebSearch()],
#     tools=[dummy_web_search_tool],
#     # tool_choice="web_search_tool",
#     tool_choice="dummy_web_search_tool", # testing
# )
QUERY_GENERATOR_MODEL_WITH_FALLBACK_AND_TOOLS = initialize_model_with_fallbacks(
    primary_model_fn=get_groq_model,
    primary_model_kwargs={"model_name": 1, "temperature": 0.7},
    fallback_model_fns=[get_groq_model, get_gemini_model],
    fallback_model_kwargs_list=[
        {"model_name": 2, "temperature": 0.7},
        {"model_name": 1, "temperature": 0.7}
    ],
    bind_tools=True,
    # tools=[WebSearch()],
    tools=[dummy_web_search_tool],
    # tool_choice="web_search_tool",
    tool_choice="dummy_web_search_tool", # testing
)


async def entity_extractor(state: KeywordState):
    """
    Extract top 1-3 entities from the user's input.

    This function processes the `state.user_input` to identify and extract
    the most relevant entities (1-3 entities). These entities will serve as
    the foundation for generating search queries for competitor analysis
    and seed keywords for Google Keyword Planner (GKP).

    Updates:
        - state.retrieved_entities: List of extracted entities.
    """
    # # Get user input from state
    # user_article: str = state["user_input"]

    # # Prepare the prompt
    # prompt: str = ENTITY_EXTRACTOR_PROMPT.format(user_article=user_article)

    # # initialize the list of retrieved entities
    # retrieved_entities: list[str] = []

    # try:
    #     # Use the model with fallback to extract entities. The appropriate model will be chosen automatically if primary fails.
    #     # type hinting doesn't work here because python isn't recognizing that structured output will be pydantic object.
    #     entities: Entities = await ENTITIES_MODEL_WITH_FALLBACK_AND_STRUCTURED.ainvoke(
    #         input=[HumanMessage(content=prompt)]
    #     )  # type: ignore

    #     # Extract the list of entities
    #     retrieved_entities: list[str] = entities.entities

    # except Exception as e:
    #     # This will only trigger if both models fail
    #     raise RuntimeError(
    #         f"Entity extraction failed with all available models: {str(e)}"
    #     ) from e

    # # Return the retrieved entities
    # print(f"Retrieved entities: {retrieved_entities}")
    
    # for testing
    entities = [
      "NIH funding cuts",
      "Ivy League universities",
      "University protests"
    ]
    return {"retrieved_entities": entities}
    # return {"retrieved_entities": retrieved_entities}


async def query_generator(state: KeywordState):
    """
    Takes user_input and retrieved_entities and generates search queries.
    If state['_web_search_results_accumulated'] has previous tool calls and their responses then it will also look at the tool response to previous queries and regenerate search queries.
    Its tool_choice parameter is set to "web_search_tool" to force the LLM to always use the web search tool.
    
    Updates:
        - state.messages: updates it with AIMessage which should have toolCall.
        - state.generated_search_queries: List of generated search queries
        - state.tool_call_count: Initializes to 0 if it doesn't exist so routeing edge can increment it after making sure a tool call was made
    """
    # check this to ensure AI made a tool call and followed instructions. this way we can add 1 to tool_call_count
    tool_call_was_made: bool = False
    
    model = QUERY_GENERATOR_MODEL_WITH_FALLBACK_AND_TOOLS
    web_search_results: str = state.get("web_search_results_accumulated", "")
    
    # testing
    print(f"\nweb_search_results: {web_search_results}")
    
    prompt = QUERY_GENERATOR_PROMPT.format(
        user_article=state["user_input"],
        entities=state["retrieved_entities"],
        web_search_results=web_search_results,
    )
    
    ai_message = await model.ainvoke([HumanMessage(content=prompt)])
    
    # get the search queries from the tool call AI made. Here if AI did not make a tool call then it will be empty. 
    # But we did everything to ensure that AI makes a tool call.
    print()
    pprint(ai_message)
    search_queries = []
    tool_calls: list[Any] = ai_message.tool_calls # type: ignore
    for t in tool_calls:
        query: str = t["args"]["query"]
        search_queries.append(query)
    
    # update tool_call_was_made to true if AI made a tool call
    if len(tool_calls) > 0:
        tool_call_was_made = True

    pprint(f"\nSearch_queries: {search_queries}")
    
    if tool_call_was_made:
        print(f"\nTool call was made: {tool_call_was_made} \n\n")
        return {
            'messages': [ai_message], 
            'generated_search_queries': search_queries,
            "tool_call_count": state.get("tool_call_count", 0) + 1
        }
    else:
        return {
            'messages': [ai_message], 
            'search_queries': search_queries,
            "tool_call_count": state.get("tool_call_count", 0)
            }

async def competitor_analysis(state: KeywordState):
    """
    This node gets the user_input, retrieved_entities and web_search_results from the state and conducts competitor analysis.
    
    Updates:
        - state.competitor_information: List of competitor data from top 5 search results (it may have upto 20 results). 
        - state.generated_search_queries: List of generated search queries (it may have upto 4 search queries so it must choose the top 2).
        - state.competitive_analysis: Competitive analysis generated by our agent after comparing our article with competitor content.  
    """
    pass

async def google_keyword_planner(state: KeywordState):
    """
    Use Google Keyword Planner (GKP) to retrieve keyword data based on the
    generated search queries.

    Steps:
        1. Call the GKP API on seed keywords and retrieve keyword data with metrics.
        2. Conducts two GKP API calls with same seed keywords but different seed url:
              - use default seed url
              - use competitor url

    Note: Make parallel calls to GKP API for lower latency as each call takes 3-8 seconds.

    Updates:
        - state.keyword_planner_data: List of keyword data retrieved from GKP.
    """
    pass


async def masterlist_and_primary_keyword_generator(state: KeywordState):
    """
    Generates a masterlist of keywords based on the GKP data. Also outputs primary and secondary keywords

    Steps:
        1. Analyze the GKP data from the previous step.
        2. We can have maximum of 50 keywords from the previous steps (25 max per GKP call).
        3. First get rid of any duplicates.
        4. Determine the relevancy of each keyword based to our user_input and competitive analysis.
        5. Look at the metrics for each relevant keyword.
        6. Pick up to 20 keywords based on the relevancy and metrics.
        7. Get a masterlist of keywords sorted by descending order. output this.

        8. Then pick 3-5 primary keywords from the masterlist.
        9. Pick 3-5 secondary keywords from the masterlist. output this as well. each with a short paragraph of quantitative and qualitative reasoning.

    Warning: LLM might not give the correct names for the keywords. Match them to original keywords and call LLM again if needed.

    Updates:
        - state.keyword_masterlist: List of refined keywords.
        - state.primary_keywords: List of primary keywords with reasoning.
        - state.secondary_keywords: List of secondary keywords with reasoning.
    """
    pass


async def suggestions_generator(state: KeywordState):
    """
    Generate the final answer with suggestions for URL slug and article headlines and line by line inserted keywords.

    Steps:
        1. Generate a suggested URL slug based on the primary keywords and competitor urls.
        2. Generate 2-3 suggested article headlines based on the primary, secondary keywords and competitor titles.
        3. Provide a final answer with keywords inserted in the article in a sentence. Neatly formatted as markdown.

    Updates:
        - state.suggested_url_slug: Suggested URL slug.
        - state.suggested_article_headlines: List of suggested article headlines.
        - state.final_answer: Final answer paragraph.
    """
    pass
