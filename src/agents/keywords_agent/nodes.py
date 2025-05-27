"""
Write all the node functions for the keywords agent here.
"""

import json
from typing import Any

from src.agents.keywords_agent.state import KeywordState
from langchain_core.messages import HumanMessage
from langgraph.config import get_stream_writer

from src.tools.google_keywords_api import GoogleKeywordsAPI
from src.utils.models_initializer import (
    initialize_model_with_fallbacks,
    get_gemini_model,
    get_groq_model,
    get_mistral_model,
    get_openai_model,
)
from src.agents.keywords_agent.prompts import (
    ENTITY_EXTRACTOR_PROMPT,
    QUERY_GENERATOR_PROMPT,
    ROUTE_QUERY_OR_ANALYSIS_PROMPT,
    COMPETITOR_ANALYSIS_AND_STRUCTURED_OUTPUT_PROMPT,
    MASTERLIST_PRIMARY_SECONDARY_KEYWORD_GENERATOR_PROMPT,
    SUGGESTION_GENERATOR_PROMPT,
)
from src.agents.keywords_agent.schemas import (
    Entities,
    RouteToQueryOrAnalysis,
    CompetitorAnalysisOutputModel,
    MasterlistAndPrimarySecondaryKeywords,
    SuggestionGeneratorModel,
)
from src.tools.web_search_tool import WebSearch


# #################
# Entity Extractor Model
# #################
ENTITIES_MODEL_WITH_FALLBACK_AND_STRUCTURED = initialize_model_with_fallbacks(
    primary_model_fn=get_mistral_model,
    primary_model_kwargs={"model_num": 2, "temperature": 0.5},
    fallback_model_fns=[get_groq_model, get_openai_model],
    fallback_model_kwargs_list=[
        {"model_num": 1, "temperature": 0.5},
        {"model_num": 1, "temperature": 0.5},
    ],
    structured_output_schema=Entities,
)

#################
# Query Generator Model
#################
QUERY_GENERATOR_MODEL_WITH_FALLBACK_AND_TOOLS = initialize_model_with_fallbacks(
    primary_model_fn=get_mistral_model,
    primary_model_kwargs={"model_num": 1, "temperature": 0.7},
    fallback_model_fns=[get_openai_model, get_openai_model],
    fallback_model_kwargs_list=[
        {"model_num": 1, "temperature": 0.7},
        {"model_num": 2, "temperature": 0.7},
    ],
    bind_tools=True,
    tools=[WebSearch()],
    tool_choice="web_search_tool",
)


##############
# Router Model
##############
ROUTER_MODEL_WITH_FALLBACK_AND_STRUCTURED = initialize_model_with_fallbacks(
    primary_model_fn=get_mistral_model,
    primary_model_kwargs={"model_num": 1, "temperature": 0.1},
    fallback_model_fns=[get_openai_model, get_groq_model],
    fallback_model_kwargs_list=[
        {"model_num": 1, "temperature": 0.1},
        {"model_num": 3, "temperature": 0.1},
    ],
    structured_output_schema=RouteToQueryOrAnalysis,
)

# #################
# # Competitor Analysis Model
# #################
COMPETITOR_ANALYSIS_MODEL_WITH_FALLBACK_AND_STRUCTURED = (
    initialize_model_with_fallbacks(
        primary_model_fn=get_openai_model,
        primary_model_kwargs={"model_num": 1, "temperature": 0.3},
        fallback_model_fns=[get_mistral_model, get_openai_model],
        fallback_model_kwargs_list=[
            {"model_num": 1, "temperature": 0.3},
            {"model_num": 2, "temperature": 0.3},
        ],
        structured_output_schema=CompetitorAnalysisOutputModel,
    )
)

##############
# # Initialize Google Keyword Planner API client
##############
gkp = GoogleKeywordsAPI()

##############
# # Masterlist and Primary Keyword Model
##############
MPS_MODEL_WITH_FALLBACK_AND_STRUCTURED = initialize_model_with_fallbacks(
    primary_model_fn=get_openai_model,
    primary_model_kwargs={"model_num": 1, "temperature": 0.5},
    fallback_model_fns=[get_mistral_model, get_openai_model],
    fallback_model_kwargs_list=[
        {"model_num": 1, "temperature": 0.5},
        {"model_num": 2, "temperature": 0.5},
    ],
    structured_output_schema=MasterlistAndPrimarySecondaryKeywords,
)

################
# # Suggestions Generator Model
################
SUGGESTIONS_MODEL_WITH_FALLBACK_AND_STRUCTURED = initialize_model_with_fallbacks(
    primary_model_fn=get_mistral_model,
    primary_model_kwargs={"model_num": 1, "temperature": 0.5},
    fallback_model_fns=[get_openai_model, get_gemini_model],
    fallback_model_kwargs_list=[
        {"model_num": 1, "temperature": 0.5},
        {"model_num": 2, "temperature": 0.5},
    ],
    structured_output_schema=SuggestionGeneratorModel,
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
    # initialize custom stream writer for langgraph to emit functions to frontend
    stream_writer = get_stream_writer()
    stream_writer(
        {
            "type": "internal",
            "event_status": "new",
            "node": "Entity Extractor",
            "content": "Extracting entities from your article to understand the topic better.",
        }
    )

    # Get user input from state
    user_article: str = state["user_input"]

    # Prepare the prompt
    prompt: str = ENTITY_EXTRACTOR_PROMPT.format(user_article=user_article)

    # initialize the list of retrieved entities
    retrieved_entities: list[str] = []

    try:
        # Use the model with fallback to extract entities. The appropriate model will be chosen automatically if primary fails.
        # type hinting doesn't work here because python isn't recognizing that structured output will be pydantic object.
        entities: Entities = await ENTITIES_MODEL_WITH_FALLBACK_AND_STRUCTURED.ainvoke(
            input=[HumanMessage(content=prompt)]
        )  # type: ignore

        # Extract the list of entities
        retrieved_entities: list[str] = entities.entities

        stream_writer(
            {
                "type": "internal",
                "event_status": "old",
                "node": "Entity Extractor",
                "content": f"Entities extracted successfully!",
            }
        )
        stream_writer(
            {
                "type": "internal_content",
                "event_status": "old",
                "node": "Entity Extractor",
                "content": retrieved_entities,
            }
        )
        return {"retrieved_entities": retrieved_entities}

    except Exception as e:
        stream_writer(
            {
                "type": "error",
                "event_status": "new",
                "node": "Entity Extractor",
                "content": f"Error encountered in Entity Extraction: {str(e)}",
            }
        )
        # if error has occured we will terminate the connection with frontend and user should see error message.
        print(f"Error encountered in Entity Extraction: {e}")


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
    # initialize custom stream writer for langgraph to emit functions to frontend
    stream_writer = get_stream_writer()
    stream_writer(
        {
            "type": "internal",
            "event_status": "new",
            "node": "Query Generator",
            "content": "Generating search queries to find your competitors...",
        }
    )

    # check this to ensure AI made a tool call and followed instructions. this way we can add 1 to tool_call_count
    tool_call_was_made: bool = False

    # initialize search queries so we can append results to it
    search_queries = []

    # get current web search results from state. This will be empty if this is the first time we are calling this node.
    web_search_results: str = state.get("web_search_results_accumulated", "")

    prompt = QUERY_GENERATOR_PROMPT.format(
        user_article=state["user_input"],
        entities=state["retrieved_entities"],
        web_search_results=web_search_results,
    )

    try:
        ai_message = await QUERY_GENERATOR_MODEL_WITH_FALLBACK_AND_TOOLS.ainvoke(
            [HumanMessage(content=prompt)]
        )

        # access tool calls array in AIMessage (tool_calls always present but maybe empty if AI didn't make a tool call and misbehaved)
        # !! we are manually extracting the tool calls, instead we COULD have done a structured output but models misbehave more often when they are provided both tools and structured output.
        tool_calls: list[Any] = ai_message.tool_calls  # type: ignore
        for t in tool_calls:
            # here "query" can be accessed because thats the exact name of the parameter for web_search_tool. If that ever changes this must change too!
            query: str = t["args"]["query"]
            search_queries.append(query)

        # update tool_call_was_made variable to true if AI made a tool call. This allows us to increment the tool_call_count in the state.
        if len(tool_calls) > 0 and len(search_queries) > 0:
            stream_writer(
                {
                    "type": "internal",
                    "event_status": "old",
                    "node": "Query Generator",
                    "content": "Queries generated successfully!",
                }
            )
            tool_call_was_made = True

        # stream these search queries to the frontend so user can see them
        stream_writer(
            {
                "type": "internal_content",
                "event_status": "old",
                "node": "Query Generator",
                "content": search_queries,
            }
        )

        if tool_call_was_made:
            return {
                # add AIMessage to 'messages' so tools_condition edge can detect the tool call and route to "tools" node.
                "messages": [ai_message],
                # we add search queries in the state so we can access them in the router_and_state_updater node. They are useful in formatting web_search_results_accumulated
                "generated_search_queries": search_queries,
                # increment the tool_call_count so we can route to "competitor_analysis" node after 2 calls (this sets an upper bound on the tool calls)
                "tool_call_count": state.get("tool_call_count", 0) + 1,
            }
        else:
            # if AI didn't make a tool call then we will not increment the tool_call_count but still initialize to 0.
            # this is the misbehaved state thus router_and_state_updater will route back to this node. Sometimes simple retries work.
            # NOTE: This can cause infinite loop if AI keeps misbehaving (unlikely but these LLMs are unpredictable).
            # TODO: add a max retry count to prevent infinite loop.
            return {
                "messages": [ai_message],
                "search_queries": search_queries,
                "tool_call_count": state.get("tool_call_count", 0),
            }

    except Exception as e:
        stream_writer(
            {
                "type": "error",
                "event_status": "new",
                "node": "Query Generator",
                "content": f"Error encountered in Query Generation: {str(e)}",
            }
        )
        print(f"Error encountered in Query Generation: {e}")


async def router_and_state_updater(state: KeywordState):
    """
    This node recieves the ToolMessage from the "tools" Node and determines whether to route to the "query_generator" or "competitor_analysis" node if enough quality competitors have been found.
    I made this into a node instead of conditional edge because I want to be able to update the "web_search_results_accumulated" state with the tool response and the search queries.

    Updates:
        - state._web_search_results_accumulated: updates it with the tool response. Adds the search queries to the tool response as well.
        - state.route_to: sets it to "competitor_analysis" or "query_generator" based on the tool response.
    """
    # initialize custom stream writer for langgraph to emit functions to frontend
    stream_writer = get_stream_writer()
    stream_writer(
        {
            "type": "internal",
            "event_status": "new",
            "node": "Query Analyzer",
            "content": "Determining if we have enough quality competitors to proceed with competitor analysis...",
        }
    )

    # if tool call count is 0 that means no tool call was made and we should route to "query_generator" node
    if state["tool_call_count"] == 0:
        stream_writer(
            {
                "type": "internal",
                "event_status": "old",
                "node": "Query Analyzer",
                "content": "Something went wrong and no query was generated by the AI. Routing back to query generator",
            }
        )
        # if we have not called the tool yet, we will call it again
        return {"route_to": "query_generator"}

    if state["tool_call_count"] >= 2:

        # if we have already called the tool twice, we will not call it again but we still need to update web_search_results with latest tool response (append to existing results)
        messages: list = state["messages"]
        web_search_results = await update_web_search_results(
            messages=messages,
            search_queries=state["generated_search_queries"],
            web_search_results_accumulated=state.get(
                "web_search_results_accumulated", ""
            ),
        )

        stream_writer(
            {
                "type": "internal",
                "event_status": "old",
                "node": "Query Analyzer",
                "content": "Found enough competitors, transferring to competitor analyst for further processing",
            }
        )
        return {
            "route_to": "competitor_analysis",
            "web_search_results_accumulated": web_search_results,
        }
    else:
        # Get the tool response from last two ToolMessages. But if only 1 tool call was made then we will only have 1 ToolMessage.
        messages: list = state["messages"]

        # update the web search results with the content from the last two ToolMessages and the corresponding search queries
        web_search_results = await update_web_search_results(
            messages=messages,
            search_queries=state["generated_search_queries"],
            web_search_results_accumulated=state.get(
                "web_search_results_accumulated", ""
            ),
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

        try:
            # invoke the router model
            router_decision: (
                RouteToQueryOrAnalysis
            ) = await ROUTER_MODEL_WITH_FALLBACK_AND_STRUCTURED.ainvoke(
                [HumanMessage(content=prompt)]
            )  # type: ignore

            # stream the decision to the frontend
            if router_decision.route == "competitor_analysis":
                stream_writer(
                    {
                        "type": "internal",
                        "event_status": "old",
                        "node": "Query Analyzer",
                        "content": "Enough quality competitors found, routing to competitor analysis node for further processing",
                    }
                )
            elif router_decision.route == "query_generator":
                stream_writer(
                    {
                        "type": "internal",
                        "event_status": "old",
                        "node": "Query Analyzer",
                        "content": "Not enough quality competitors found, routing back to query generator node to generate more queries and find more competitors",
                    }
                )

            return {
                "route_to": router_decision.route,
                "web_search_results_accumulated": web_search_results,
            }

        except Exception as e:
            stream_writer(
                {
                    "type": "error",
                    "event_status": "new",
                    "node": "Query Analyzer",
                    "content": f"Error occurred in query analysis node: {e}",
                }
            )
            print(f"Error occurred in query analysis node: {e}")


async def competitor_analysis(state: KeywordState):
    """
    This node gets the user_input, retrieved_entities and web_search_results_accumulated from the state and conducts competitor analysis.

    Updates:
        - state.competitor_information: List of competitor data from top 5 search results (it may have upto 20 results).
        - state.generated_search_queries: List of generated search queries (it may have upto 4 search queries so it must choose the top 2).
        - state.competitive_analysis: Competitive analysis generated by our agent after comparing our article with competitor content.
        - state.web_search_results_accumulated: Cleans up the space by setting it to "" so garbage collector can clean it up.
    """
    # initialize custom stream writer for langgraph to emit functions to frontend
    stream_writer = get_stream_writer()
    stream_writer(
        {
            "type": "internal",
            "event_status": "new",
            "node": "Competitor Analysis",
            "content": "Conducting competitor analysis on the search results to find top competitors and analyze their content. This may take sometime because there is alot to analyze...",
        }
    )

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
        response: (
            CompetitorAnalysisOutputModel
        ) = await COMPETITOR_ANALYSIS_MODEL_WITH_FALLBACK_AND_STRUCTURED.ainvoke(
            [HumanMessage(content=prompt)]
        )  # type: ignore

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

        # stream the competitor information to the frontend
        stream_writer(
            {
                "type": "internal",
                "event_status": "old",
                "node": "Competitor Analysis",
                "content": "Phew! Competitor analysis completed successfully yay!",
            }
        )

        # this data will be used by frontend in the answer box (it will be stored until all internal steps finish and then will be displayed)
        stream_writer(
            {
                "type": "answer",
                "event_status": "new",
                "node": "Competitor Analysis",
                "content": {
                    "competitor_information": competitor_information,
                    "competitive_analysis": competitive_analysis,
                },
            }
        )

        # update the state
        return {
            "competitor_information": competitor_information,
            "generated_search_queries": generated_search_queries,
            "competitive_analysis": competitive_analysis,
            # set to "" to clean up space
            "web_search_results_accumulated": "",
        }

    except Exception as e:
        print(f"Error occurred in competitor analysis node: {e}")
        stream_writer(
            {
                "type": "error",
                "event_status": "new",
                "node": "Competitor Analysis",
                "content": f"Error occured in competitor analysis node: {str(e)}",
            }
        )


async def google_keyword_planner1(state: KeywordState):
    """
    Use Google Keyword Planner API to get keyword data for our article. We make 2 parallel calls, this node and google_keyword_planner2 node run in one super step in langgraph.
    We will use state["retrieved_entities"] as seed keywords for both calls but this node uses first url in the competitor_information list and the other node uses the second url in the list.

    Updates:
        - state.planner_list1: List of keyword data from the first GKP call
    """
    # custom stream writer for langgraph to emit functions to frontend
    stream_writer = get_stream_writer()
    stream_writer(
        {
            "type": "internal",
            "event_status": "new",
            "node": "Google Keyword Planner",
            "content": "Using Google keyword planner to get keyword recommendations for your article. Running parallel calls to get many different keywords",
        }
    )

    # Get the seed keywords from the state
    seed_keywords: list[str] = state.get("retrieved_entities", [])

    # Get the competitor information list from the state
    competitor_information: list[dict[str, str | int]] = state.get(
        "competitor_information", []
    )

    try:
        # Get the first URL from the competitor information (assumes at least one entry exists)
        top_url: str = competitor_information[0]["url"]  # type: ignore

        # Fetch keyword planner data using the helper function
        planner_list1: list[dict[str, str | int]] = await fetch_gkp_keywords(
            seed_keywords=seed_keywords, url=top_url
        )

        # Update the state with the results
        return {"planner_list1": planner_list1}

    except Exception as e:
        print(f"Error occurred in Google Keyword Planner 1 node: {e}")
        stream_writer(
            {
                "type": "error",
                "event_status": "new",
                "node": "Google Keyword Planner 1",
                "content": f"Error occurred in Google Keyword Planner 1 node: {str(e)}",
            }
        )


async def google_keyword_planner2(state: KeywordState):
    """
    Use Google Keyword Planner API to get keyword data for our article. We make 2 parallel calls, this node and google_keyword_planner1 node run in one super step in langgraph.
    We will use state["retrieved_entities"] as seed keywords for both calls but this node uses second url in the competitor_information list and the other node uses the first url in the list.

    Updates:
        - state.planner_list2: List of keyword data from the second GKP call
    """
    stream_writer = get_stream_writer()

    # Get the seed keywords from the state
    seed_keywords: list[str] = state.get("retrieved_entities", [])

    # Get the competitor information list from the state
    competitor_information: list[dict[str, str | int]] = state.get(
        "competitor_information", []
    )
    try:
        # We need to find the URL for the competitor with rank=2.
        # We cannot simply take the second object in the list because sometimes there are multiple objects with rank=1 (LLM might have misbehaved).
        # Therefore, we loop through the array and select the first object where rank==2. This should be quick though it won't really have O(n) complexity.
        second_url: str = ""
        for competitor in competitor_information:
            rank = competitor.get("rank", None)
            # ensure rank is not None and equal 2
            if isinstance(rank, int) and rank == 2:
                second_url: str = competitor["url"]  # type: ignore
                break

        # Fetch keyword planner data using the helper function
        planner_list2: list[dict[str, str | int]] = await fetch_gkp_keywords(
            seed_keywords=seed_keywords, url=second_url
        )

        # Update the state with the results
        return {"planner_list2": planner_list2}

    except Exception as e:
        print(f"Error occurred in Google Keyword Planner 2 node: {e}")
        stream_writer(
            {
                "type": "error",
                "event_status": "new",
                "node": "Google Keyword Planner 2",
                "content": f"Error occurred in Google Keyword Planner 2 node: {str(e)}",
            }
        )


async def keyword_data_synthesizer(state: KeywordState):
    """
    Merges, Deduplicates and Sorts the keyword planner data from both GKP calls and combines them into a single list.
    \nMerge and Deduplication happens in O(n+m) using hash set where n and m are the lengths of the two lists.
    \nSorting happens in O(nlogn) using Timsort (Python's built-in sort algorithm) where n is the length of the combined list.
    \nThis is a single step in the langgraph and runs after both GKP calls are completed.

    Updates:
        - state.keyword_planner_data: Combined and sorted list of keyword data from both GKP calls.
    """
    stream_writer = get_stream_writer()

    # Retrieve the two lists of keyword data from the state, defaulting to empty lists if not present (though it should be present)
    planner_list1: list[dict[str, int | str | dict[str, int]]] = state.get(
        "planner_list1", []
    )
    planner_list2: list[dict[str, int | str | dict[str, int]]] = state.get(
        "planner_list2", []
    )
    size: int = len(planner_list1) + len(planner_list2)

    stream_writer(
        {
            "type": "internal",
            "event_status": "old",
            "node": "Google Keyword Planner",
            "content": f"Google Keyword Planner recommendations received! Found a total of {size} keywords.",
        }
    )

    stream_writer(
        {
            "type": "internal",
            "event_status": "new",
            "node": "Keywords Synthesizer",
            "content": f"Now combining and deduplicating those {size} keywords to get unique keywords ...",
        }
    )

    # Initialize a set to track unique keyword texts for deduplication
    seen_keywords: set[str] = set()

    # Initialize a list to store the combined and deduplicated keywords
    combined_keywords: list[dict[str, int | str | dict[str, int]]] = []

    # Merge and deduplicate both lists in a single pass
    for keyword_list in (planner_list1, planner_list2):
        # iterate through the objects in each list
        for keyword_data in keyword_list:
            keyword_text: str = str(keyword_data.get("text", ""))

            # Only add the keyword if it has not been seen before and is not empty
            if keyword_text and keyword_text not in seen_keywords:
                seen_keywords.add(keyword_text)
                combined_keywords.append(keyword_data)

    # Sort the combined list by 'average_monthly_searches' in descending order
    try:
        # the key will be an int but type checker isn't identifying that GKP parser will always only add int to this field so we use type: ignore
        combined_keywords.sort(
            key=lambda x: int(x.get("average_monthly_searches", 0)),  # type: ignore
            reverse=True,
        )

        stream_writer(
            {
                "type": "internal",
                "event_status": "old",
                "node": "Keywords Synthesizer",
                "content": f"Combined and sorted all keywords, finalized {len(combined_keywords)} unique keywords for your article!",
            }
        )

        # Return the updated state with the combined keyword planner data
        return {
            "keyword_planner_data": combined_keywords,
            # clear the planner lists to free up memory
            "planner_list1": [],
            "planner_list2": [],
        }
    except Exception as sort_error:
        # Handle any sorting errors gracefully and print a meaningful message
        print(f"Error sorting combined keyword data: {sort_error}")
        stream_writer(
            {
                "type": "error",
                "event_status": "new",
                "node": "Keywords Synthesizer",
                "content": f"Error occurred while sorting keywords: {str(sort_error)}",
            }
        )


async def masterlist_and_primary_keyword_generator(state: KeywordState):
    """
    Generates a masterlist of keywords based on the GKP data. Also outputs primary and secondary keywords

    Steps:
        1. Analyze the GKP data from the previous step.
        2. We can have maximum of 50 keywords from the previous steps (25 max per GKP call).
        3. Determine the relevancy of each keyword based on our user_input and competitor_information.
        6. Pick up to 20 keywords based on the relevancy and metrics.
        7. Get a masterlist of keywords sorted by descending order: list of objects has {text, monthly_searches, competition, competition_index, relevancy_score}.

        8. Then pick 3-5 primary keywords from the masterlist.
        9. Pick 3-5 secondary keywords from the masterlist. output this as well. each with a short paragraph of quantitative and qualitative reasoning.

    Updates:
        - state.keyword_masterlist: List of refined keywords.
        - state.primary_keywords: List of primary keywords with reasoning.
        - state.secondary_keywords: List of secondary keywords with reasoning.
    """
    stream_writer = get_stream_writer()
    stream_writer(
        {
            "type": "internal",
            "event_status": "new",
            "node": "Masterlist and Primary Keyword Generator",
            "content": "Generating a masterlist of most relevant keywords for your article and selecting SEO optimized primary and secondary keywords. Sometimes this takes a few seconds to effectively extract everything...",
        }
    )

    # extract all the input data from the state
    user_input: str = state.get("user_input", "")
    retrieved_entities: list[str] = state.get("retrieved_entities", [])
    competitor_information: list[dict[str, str | int]] = state.get(
        "competitor_information", []
    )
    search_queries: list[str] = state.get("generated_search_queries", [])
    competitor_analysis: str = state.get("competitive_analysis", "")
    keyword_planner_data: list[dict[str, int | str | dict[str, int]]] = state.get(
        "keyword_planner_data", []
    )
    # format some input vars for inserting into the prompt as string
    keyword_planner_data_str: str = json.dumps(keyword_planner_data, indent=2)

    # initialize the output variables
    keyword_masterlist: list[dict[str, str]] = []
    primary_keywords: list[dict[str, str]] = []
    secondary_keywords: list[dict[str, str]] = []

    # prepare the prompt for the masterlist and primary keyword generator model
    prompt = MASTERLIST_PRIMARY_SECONDARY_KEYWORD_GENERATOR_PROMPT.format(
        user_article=user_input,
        entities=retrieved_entities,
        generated_search_queries=search_queries,
        competitor_information=competitor_information,
        competitor_analysis=competitor_analysis,
        keyword_planner_data=keyword_planner_data_str,
    )

    try:
        response: (
            MasterlistAndPrimarySecondaryKeywords
        ) = await MPS_MODEL_WITH_FALLBACK_AND_STRUCTURED.ainvoke(
            [HumanMessage(content=prompt)]
        )  # type: ignore

        # Convert each Pydantic model in the lists to a dict for state compatibility
        keyword_masterlist = [item.model_dump() for item in response.keyword_masterlist]
        primary_keywords = [item.model_dump() for item in response.primary_keywords]
        secondary_keywords = [item.model_dump() for item in response.secondary_keywords]

        stream_writer(
            {
                "type": "internal",
                "event_status": "old",
                "node": "Masterlist and Primary Keyword Generator",
                "content": f"Generated masterlist with {len(keyword_masterlist)} keywords, selected {len(primary_keywords)} primary and {len(secondary_keywords)} secondary keywords",
            }
        )

        # stream the results to the frontend so that they can be displayed in the answer box
        stream_writer(
            {
                "type": "answer",
                "event_status": "new",
                "node": "Masterlist and Primary Keyword Generator",
                "content": {
                    "keyword_masterlist": keyword_masterlist,
                    "primary_keywords": primary_keywords,
                    "secondary_keywords": secondary_keywords,
                },
            }
        )

        # update the state with the results
        return {
            "keyword_masterlist": keyword_masterlist,
            "primary_keywords": primary_keywords,
            "secondary_keywords": secondary_keywords,
        }

    except Exception as e:
        print(f"Error occurred in masterlist and primary keyword generator node: {e}")
        stream_writer(
            {
                "type": "error",
                "event_status": "new",
                "node": "Masterlist and Primary Keyword Generator",
                "content": f"Error occurred in masterlist and primary keyword generator node: {str(e)}",
            }
        )


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
    stream_writer = get_stream_writer()
    stream_writer(
        {
            "type": "internal",
            "event_status": "new",
            "node": "Suggestions Generator",
            "content": "Generating final suggestions for URL slug, article headlines, and final answer using all the information collected so far...",
        }
    )

    # get input data from the state
    user_input: str = state.get("user_input", "")
    primary_keywords: list[dict[str, str]] = state.get("primary_keywords", [])
    secondary_keywords: list[dict[str, str]] = state.get("secondary_keywords", [])
    competitor_information: list[dict[str, str | int]] = state.get(
        "competitor_information", []
    )
    competitor_analysis: str = state.get("competitive_analysis", "")

    # initialize the output variables
    suggested_url_slug: str = ""
    suggested_article_headlines: list[str] = []
    final_answer: str = ""

    # prepare the prompt for the suggestions generator model
    prompt = SUGGESTION_GENERATOR_PROMPT.format(
        user_article=user_input,
        primary_keywords=primary_keywords,
        secondary_keywords=secondary_keywords,
        competitor_information=competitor_information,
        competitor_analysis=competitor_analysis,
    )

    try:
        response: (
            SuggestionGeneratorModel
        ) = await SUGGESTIONS_MODEL_WITH_FALLBACK_AND_STRUCTURED.ainvoke(
            [HumanMessage(content=prompt)]
        )  # type: ignore

        # extract the output variables from the response
        suggested_url_slug = response.suggested_url_slug
        suggested_article_headlines = response.suggested_article_headlines
        final_answer = response.final_suggestions

        # stream the suggestions to the frontend
        stream_writer(
            {
                "type": "internal",
                "event_status": "old",
                "node": "Suggestions Generator",
                "content": f"Generated suggestion susccessfully!",
            }
        )

        # stream the answer as well so that it can be displayed in the answer box
        stream_writer(
            {
                "type": "answer",
                "event_status": "new",
                "node": "Suggestions Generator",
                "content": {
                    "suggested_url_slug": suggested_url_slug,
                    "suggested_article_headlines": suggested_article_headlines,
                    "final_answer": final_answer,
                },
            }
        )

        # update the state with the results
        return {
            "suggested_url_slug": suggested_url_slug,
            "suggested_article_headlines": suggested_article_headlines,
            "final_answer": final_answer,
        }

    except Exception as e:
        print(f"Error occurred in suggestions generator node: {e}")
        stream_writer(
            {
                "type": "error",
                "event_status": "new",
                "node": "Suggestions Generator",
                "content": f"Error occurred in suggestions generator node: {str(e)}",
            }
        )


#################
# # utility functions to help update web search. since we needed it twice i made it a function
#################


async def update_web_search_results(
    messages: list, search_queries: list[str], web_search_results_accumulated: str
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


async def fetch_gkp_keywords(
    seed_keywords: list[str], url: str
) -> list[dict[str, str | int]]:
    """
    Fetch keyword data from Google Keyword Planner API for given seed keywords and a competitor URL.

    This helper function is used by both google_keyword_planner1 and google_keyword_planner2 nodes to avoid code duplication.
    It performs an asynchronous API call to the Google Keyword Planner and returns the resulting keyword data.

    Args:
        seed_keywords (list[str]): List of seed keywords to use for the API call.
        url (str): The competitor URL to use for the API call.

    Returns:
        list[dict[str, str | int]]: List of keyword data dictionaries returned by the API.
    """
    planner_list: list[dict[str, str | int]] = []
    try:
        # Await the async API call to ensure non-blocking execution in LangGraph's async loop
        response: list[dict[str, str | int]] = await gkp.generate_keywords(
            keywords=seed_keywords, url=url
        )
        planner_list = response
    except Exception as e:
        print(f"Error occurred in fetch_gkp_keywords: {e}")
    return planner_list
