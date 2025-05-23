
from src.agents.keywords_agent.schemas import Entities, SearchQueries, keywordMaster_primary_secondarylist, suggestiongenerator
from src.agents.keywords_agent.prompts import (
    ENTITY_EXTRACTOR_PROMPT,
    COMPETITOR_ANALYST_PROMPT,
    MASTERLIST_AND_PRIMARY_KEYWORD_GENERATOR_PROMPT,
    SUGGESTIONS_GENERATOR_PROMPT,

)



# #################
# Initialize models for Competitor Analyst Node
# #################
LISTS_OF_KEYWORDS_PRIMARY_MODEL = get_gemini_model(
    model_name=2, temperature=0.6
).with_structured_output(schema=suggestiongenerator)

LISTS_OF_KEYWORDS_FALLBACK_MODEL1 = get_gemini_model(
    model_name=3, temperature=0.6
).with_structured_output(schema=suggestiongenerator)

LISTS_OF_KEYWORDS_FALLBACK_MODEL2 = get_groq_model(
    model_name=2, temperature=0.6
).with_structured_output(schema=suggestiongenerator)

# Create a reusable model with fallback mechanism for lists_of_keywords
LISTS_OF_KEYWORDS_MODEL_WITH_FALLBACK = LISTS_OF_KEYWORDS_PRIMARY_MODEL.with_fallbacks(
    fallbacks=[LISTS_OF_KEYWORDS_FALLBACK_MODEL1, LISTS_OF_KEYWORDS_FALLBACK_MODEL2],
    exceptions_to_handle=(Exception),
)

# #################
# Initialize models for Suggestion Generator Node
# #################
SUGGESTION_GENERATOR_PRIMARY_MODEL = get_gemini_model(
    model_name=2, temperature=0.6
).with_structured_output(schema=keywordMaster_primary_secondarylist)

SUGGESTION_GENERATOR_FALLBACK_MODEL1 = get_gemini_model(
    model_name=3, temperature=0.6
).with_structured_output(schema=keywordMaster_primary_secondarylist)

SUGGESTION_GENERATOR_FALLBACK_MODEL2 = get_groq_model(
    model_name=2, temperature=0.6
).with_structured_output(schema=keywordMaster_primary_secondarylist)

# Create a reusable model with fallback mechanism for lists_of_keywords
SUGGESTION_GENERATOTR_MODEL_WITH_FALLBACK = SUGGESTION_GENERATOR_PRIMARY_MODEL.with_fallbacks(
    fallbacks=[SUGGESTION_GENERATOR_FALLBACK_MODEL1, SUGGESTION_GENERATOR_FALLBACK_MODEL2],
    exceptions_to_handle=(Exception),
)





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
    # Get the GKP data, entities, and user input from state
    gkp_data: list[dict[str, Any]] = state["keyword_planner_data"]
    entities: list[str] = state["retrieved_entities"]
    user_article: str = state["user_input"]
    competitive_analysis: str = state["competitive_analysis"]

    # Prepare the prompt & call it 
    prompt: str = MASTERLIST_AND_PRIMARY_KEYWORD_GENERATOR_PROMPT.format(
        user_article=user_article,
        entities=entities,
        gkp_data=gkp_data,
        competitive_analysis= competitive_analysis,
    )

    # Initialize the lists of keywords
    keyword_masterlist: list[dict[str, str]] = []
    primary_keywords: list[dict[str, str]] = []
    secondary_keywords: list[dict[str, str]] = []

    try:

        lists_of_keywords: (keywordMaster_primary_secondarylist) = await (
            LISTS_OF_KEYWORDS_MODEL_WITH_FALLBACK.ainvoke(
                input=[HumanMessage(content=prompt)]
            )
        )

        # Extract the lists of keywords
        keyword_masterlist: list[dict[str,str]] = lists_of_keywords.masterlist_keywords
        primary_keywords: list[dict[str,str]] = lists_of_keywords.primary_keywords
        secondary_keywords: list[dict[str,str]] = lists_of_keywords.secondary_keywords

    except Exception as e:
        raise RuntimeError(
            f"Masterlist and primary keyword generation failed: {str(e)}"
        ) from e 
    
    # Return the retrieved lists of keywords
    print(f"Keywords_Masterlist: {keyword_masterlist}")
    print(f"Primary_keywords: {primary_keywords}")
    print(f"Secondary_keywords:{secondary_keywords}")

    # update the state for the keywords_masterlist, primary_keywords and secondary_keywords
    return {
        "keyword_masterlist": keyword_masterlist,
        "primary_keywords": primary_keywords,
        "secondary_keywords": secondary_keywords
    }




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
    # Get the input from state 
    user_article: str = state["user_input"]
    competitor_information: list[dict[str,Any]] = state["competitor_information"]
    primary_keywords: list[dict[str,str]] = state["primary_keywords"]
    secondary_keywords: list[dict[str,str]] = state["secondary_keywords"]

    # Compile the prompt & call it
    prompt: str = SUGGESTIONS_GENERATOR_PROMPT.format(
        user_article=user_article, 
        competitor_information=competitor_information,
        primary_keywords=primary_keywords,
        secondary_keywords=secondary_keywords,
    )

    # Initialize the suggestions elements
    suggested_url_slug: str = ""
    suggested_article_headlines: list[str] = []
    final_answer: str = ""

    try:

        suggestions: suggestiongenerator = await(
            SUGGESTION_GENERATOTR_MODEL_WITH_FALLBACK.ainvoke(
                input=[HumanMessage(content=prompt)]
            )
        )
        # Extract the suggestions

        suggested_url_slug: str = suggestions.suggested_url_slug
        suggested_article_headlines: list[str] = suggestions.suggested_article_headlines
        final_answer: str = suggestions.final_answer
    except Exception as e:
        raise RuntimeError(
            f"Suggestions generation failed: {str(e)}"
        ) from e 
    
    # Return the suggestions
    print(f"Suggested URL Slug: {suggested_url_slug}")
    print(f"Suggested Article Headlines: {suggested_article_headlines}")
    print(f"Final Answer: {final_answer}")
    return {
        "suggested_url_slug": suggested_url_slug,
        "suggested_article_headlines": suggested_article_headlines,
        "final_answer": final_answer
    }


