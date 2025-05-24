"""
Write all the node functions for the keywords agent here.
"""

from pprint import pprint
from typing import Any
from src.agents.keywords_agent.state import KeywordState
from langchain_core.messages import HumanMessage

# Entity Extractor related imports
from src.utils.models_initializer import (
    initialize_model_with_fallbacks, 
    get_gemini_model, 
    get_groq_model,
    get_mistral_model,
    get_openai_model
)
from src.agents.keywords_agent.prompts import (
    ENTITY_EXTRACTOR_PROMPT,
    QUERY_GENERATOR_PROMPT,
    ROUTE_QUERY_OR_ANALYSIS_PROMPT,
    COMPETITOR_ANALYSIS_AND_STRUCTURED_OUTPUT_PROMPT
)
from src.agents.keywords_agent.schemas import (
    Entities, 
    RouteToQueryOrAnalysis,
    CompetitorAnalysisOutputModel
)
from src.tools.web_search_tool import WebSearch, dummy_web_search_tool


# #################
# Entity Extractor Model
# #################
ENTITIES_MODEL_WITH_FALLBACK_AND_STRUCTURED = initialize_model_with_fallbacks(
    primary_model_fn=get_gemini_model,
    primary_model_kwargs={"model_name": 2, "temperature": 0.5},
    fallback_model_fns=[get_mistral_model, get_openai_model],
    fallback_model_kwargs_list=[
        {"model_name": 1, "temperature": 0.5},
        {"model_name": 1, "temperature": 0.5}
    ],
    structured_output_schema=Entities,
)

#################
# Query Generator Model
#################
QUERY_GENERATOR_MODEL_WITH_FALLBACK_AND_TOOLS = initialize_model_with_fallbacks(
    primary_model_fn=get_mistral_model,
    primary_model_kwargs={"model_name": 1, "temperature": 0.7},
    fallback_model_fns=[get_openai_model, get_openai_model],
    fallback_model_kwargs_list=[
        {"model_name": 1, "temperature": 0.7},
        {"model_name": 2, "temperature": 0.7}
    ],
    bind_tools=True,
    # tools=[WebSearch()],
    tools=[dummy_web_search_tool], # testing
    # tool_choice="web_search_tool",
    tool_choice="dummy_web_search_tool", # testing
)


##############
# Router Model
##############
ROUTER_MODEL_WITH_FALLBACK_AND_STRUCTURED = initialize_model_with_fallbacks(
    primary_model_fn=get_mistral_model,
    primary_model_kwargs={"model_name": 1, "temperature": 0.1},
    fallback_model_fns=[get_openai_model, get_groq_model],
    fallback_model_kwargs_list=[
        {"model_name": 1, "temperature": 0.1},
        {"model_name": 3, "temperature": 0.1}
    ],
    structured_output_schema=RouteToQueryOrAnalysis
)

# #################
# # Competitor Analysis Model
# #################
COMPETITOR_ANALYSIS_MODEL_WITH_FALLBACK_AND_STRUCTURED = initialize_model_with_fallbacks(
    primary_model_fn=get_openai_model,
    primary_model_kwargs={"model_name": 2, "temperature": 0.3},
    fallback_model_fns=[get_mistral_model, get_openai_model],
    fallback_model_kwargs_list=[
        {"model_name": 1, "temperature": 0.3},
        {"model_name": 1, "temperature": 0.3}
    ],
    structured_output_schema=CompetitorAnalysisOutputModel,
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
      "Undergrad Employment",
      "College Students Unemployment",
      "Undergrad Job Market",
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
    # initialize search queries so we can append results to it
    search_queries = []
    
    # access tool calls array in AIMessage (its always present but maybe empty if AI didn't make a tool call and misbehaved)
    tool_calls: list[Any] = ai_message.tool_calls # type: ignore
    for t in tool_calls:
        # "query" below can be accessed because thats the exact name of the parameter for web_search_tool. If that ever changes this must change too!
        query: str = t["args"]["query"]
        search_queries.append(query)
    
    # update tool_call_was_made variable to true if AI made a tool call. This allows us to increment the tool_call_count in the state.
    if len(tool_calls) > 0:
        tool_call_was_made = True

    pprint(f"\nSearch_queries: {search_queries}\n")
    
    if tool_call_was_made:
        return {
            # add to 'messages' so tools_condition edge can detect the tool call and route to "tools" node.
            'messages': [ai_message], 
            # we add search queries in the state so we can access them in the router_and_state_updater node. They are useful in formatting web_search_results_accumulated
            'generated_search_queries': search_queries,
            # we increment the tool_call_count so we can route to "competitor_analysis" node after 2 calls.
            "tool_call_count": state.get("tool_call_count", 0) + 1
        }
    else:
        # if AI didn't make a tool call then we will not increment the tool_call_count but still initialize to 0.
        # this is the misbehaved state and we will route back to "entity_extractor" node to run this node again. Sometimes simple retries work. This routing is done through tools_condition edge when it doesn't detect a tool call in messages key.
        return {
            'messages': [ai_message], 
            'search_queries': search_queries,
            "tool_call_count": state.get("tool_call_count", 0)
            }

async def router_and_state_updater(state: KeywordState):
    """
    This node recieves the ToolMessage from the ToolNode and determines whether to route to the "query_generator" or "competitor_analysis" node.
    I made this into a node instead of conditional edge because I want to be able to update the state with the tool response and the search queries.
    
    Updates:
        - state._web_search_results_accumulated: updates it with the tool response. Adds the search queries to the tool response as well.
        - state.route_to: sets it to "competitor_analysis" or "query_generator" based on the tool response. 
    """
    # if tool call count is 0 that means no tool call was made and we should route to "query_generator" node
    if state["tool_call_count"] == 0:
        print("\n\nTool call count is 0. Routing to query_generator node.\n\n")
        # if we have not called the tool yet, we will call it again
        return {"route_to": "query_generator"}
    
    if state["tool_call_count"] >= 2:
        # if we have already called the tool twice, we will not call it again but we still need to update web_search_results with latest tool response (append to existing results)
        messages: list = state["messages"]
        web_search_results = update_web_search_results(
            messages=messages,
            search_queries=state["generated_search_queries"],
            web_search_results_accumulated=state.get("web_search_results_accumulated", ""),
        )
        
        print("\n\nTool call count is 2. Routing to competitor_analysis node.\n\n")
        return {"route_to": "competitor_analysis", "web_search_results_accumulated": web_search_results}
    else:              
        # Get the tool response from last two ToolMessages. But if only 1 tool call was made then we will only have 1 ToolMessage.
        messages: list = state["messages"]
        
        # update the web search results with the content from the last two ToolMessages and the corresponding search queries
        web_search_results = update_web_search_results(
            messages=messages,
            search_queries=state["generated_search_queries"],
            web_search_results_accumulated=state.get("web_search_results_accumulated", ""),
        )
        
        # get user input and entities as well
        user_input: str = state.get("user_input", "")
        retrieved_entities: list[str] = state.get("retrieved_entities", [])
        
        # prepare prompt for the router model
        prompt = ROUTE_QUERY_OR_ANALYSIS_PROMPT.format(
            user_article=user_input,
            entities=retrieved_entities,
            web_search_results=web_search_results,
        )
        
        # invoke the router model
        router_decision: RouteToQueryOrAnalysis = await ROUTER_MODEL_WITH_FALLBACK_AND_STRUCTURED.ainvoke(
            [HumanMessage(content=prompt)]
        ) # type: ignore

        return {
            "route_to": router_decision.route,
            "web_search_results_accumulated": web_search_results,
        }

    
async def competitor_analysis(state: KeywordState):
    """
    This node gets the user_input, retrieved_entities and web_search_results_accumulated from the state and conducts competitor analysis.
    
    Updates:
        - state.competitor_information: List of competitor data from top 5 search results (it may have upto 20 results). 
        - state.generated_search_queries: List of generated search queries (it may have upto 4 search queries so it must choose the top 2).
        - state.competitive_analysis: Competitive analysis generated by our agent after comparing our article with competitor content.  
    """
    # first get the input variables from the state
    user_input: str = state.get("user_input", "")
    retrieved_entities: list[str] = state.get("retrieved_entities", [])
    web_search_results: str = state.get("web_search_results_accumulated", "")
    
    # prepare the prompt for the competitor analysis model
    prompt = COMPETITOR_ANALYSIS_AND_STRUCTURED_OUTPUT_PROMPT.format(
        user_article=user_input,
        entities=retrieved_entities,
        web_search_results=web_search_results,
    )
    
    # initialize the output variables
    generated_search_queries: list[str] = []
    competitor_information: list[dict[str, str | int]] = []
    competitive_analysis: str = ""
    
    # now invoke the model
    try:
        # response should of type CompetitorAnalysisOutputModel
        response: CompetitorAnalysisOutputModel = await COMPETITOR_ANALYSIS_MODEL_WITH_FALLBACK_AND_STRUCTURED.ainvoke(
            [HumanMessage(content=prompt)]
        ) # type: ignore

        # extract the output variables from the response
        generated_search_queries = response.search_queries
        competitive_analysis = response.competitive_analysis
        
        # loop through the web search results and extract the data in our format
        for result in response.web_search_results:
            # create a dictionary for each result
            competitor_info = {
                "rank": result.rank,
                "url": result.url,
                "title": result.title,
                "published_date": result.published_date,
                "highlights": result.highlights,
            }
            # append the dictionary to the list
            competitor_information.append(competitor_info)
        
    except Exception as e:
        print(f"Error occurred in competitor analysis node: {e}")
        
    # update the state
    return {
        "competitor_information": competitor_information,
        "generated_search_queries": generated_search_queries,
        "competitive_analysis": competitive_analysis
    }

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

# utility function to help update web search. since we needed it twice i made it a function

def update_web_search_results(
    messages: list,
    search_queries: list[str],
    web_search_results_accumulated: str
) -> str:
    """
    Update the accumulated web search results with the content from the last two ToolMessages and the corresponding search queries.

    This function extracts the content from the last two ToolMessages in the messages list and appends them to the accumulated web search results,
    associating each tool response with its corresponding search query.

    Args:
        messages (list): List of ToolMessage objects, each with a 'content' attribute.
        search_queries (list[str]): List of generated search queries.
        web_search_results_accumulated (str): The previously accumulated web search results.

    Returns:
        str: The updated web search results string.
    """
    # Initialize variables to store the content of the last two tool responses
    first_tool_response: str = ""
    second_tool_response: str = ""

    # Calculate the starting index (2 before the last message)
    start_index: int = max(len(messages) - 2, 0)

    # Loop through the last two messages and extract their content
    for index in range(start_index, len(messages)):
        message = messages[index]
        # Ensure the message has a 'content' attribute so that we know its an output from a ToolMessage
        if hasattr(message, "content"):
            if index == start_index:
                first_tool_response = message.content
            else:
                second_tool_response = message.content

    # Start with the previously accumulated web search results
    web_search_results: str = web_search_results_accumulated

    # If there was only one tool call made, then len(search_queries) will be 1 and we will only have second_tool_response based on the for loop above.
    if len(search_queries) == 1:
        web_search_results = (
            web_search_results
            + f"\n\nSearch Query: {search_queries[0]}\n"
            + f"\n{second_tool_response}"
        )
    elif len(search_queries) == 2:
        web_search_results = (
            web_search_results
            + f"\n\nSearch Query: {search_queries[0]}\n"
            + f"{first_tool_response}\n\nSearch Query: {search_queries[1]}\n"
            + second_tool_response
        )

    return web_search_results
