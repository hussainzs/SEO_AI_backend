"""
Write all the node functions for the keywords agent here.
"""
from src.agents.keywords_agent.state import KeywordState

def entity_extractor(state: KeywordState):
    """
    Extract top 1-3 entities from the user's input.

    This function processes the `state.user_input` to identify and extract
    the most relevant entities (1-3 entities). These entities will serve as
    the foundation for generating search queries for competitor analysis
    and seed keywords for Google Keyword Planner (GKP).

    Updates:
        - state.retrieved_entities: List of extracted entities.
    """
    pass


def competitor_analyst(state: KeywordState):
    """
    Perform a reflective analysis to generate search queries, retrieve competitor
    information, and conduct a competitive analysis.

    Steps:
        1. Generate search queries based on the retrieved entities.
        2. Make tool calls to Tavily/Exa to fetch competitor information.
        3. Reflect on the tool results to determine if true competitive articles
           are found. If not, retry tool calls (maximum of 2 attempts).
        4. Conduct a competitive analysis based on the retrieved data.

    Updates:
        - state.generated_search_queries: List of generated search queries.
        - state.competitor_information: List of competitor data retrieved from tools.
        - state.competitive_analysis: Summary of the competitive analysis.
    """
    pass


def google_keyword_planner(state: KeywordState):
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

def masterlist_and_primary_keyword_generator(state: KeywordState):
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

def suggestions_generator(state: KeywordState):
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
