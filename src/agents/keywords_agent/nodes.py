"""
Write all the node functions for the keywords agent here.
"""
from src.agents.keywords_agent.state import KeywordState

def entity_extractor(state: KeywordState):
    """
    Extract top 1-3 entities from state['user_input'].
    \nThese entities will act as basis for the search query generation for competitor analysis and seed keywords for Google Keyword Planner (GKP).

    Updates the state['retrieved_entities'] with the extracted entities.
    """
    # TODO: Implement entity extraction logic
    pass