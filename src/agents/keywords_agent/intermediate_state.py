# Global variables to store intermediate state during graph execution
original_article_draft: str = ""
sentence_level_suggestions: str = ""

def set_original_article_draft(draft: str) -> None:
    """
    Set the original article draft that will be used for full article generation.
    
    Args:
        draft (str): The original article draft content provided by the user.
    """
    global original_article_draft
    original_article_draft = draft
    
def set_sentence_level_suggestions(suggestions: str) -> None:
    """
    Set the sentence level suggestions generated during the keyword analysis workflow.
    
    Args:
        suggestions (str): The sentence level suggestions content for article improvement.
    """
    global sentence_level_suggestions
    sentence_level_suggestions = suggestions

def get_original_article_draft() -> str:
    """
    Retrieve the original article draft.
    
    Returns:
        str: The original article draft content, or empty string if not set.
    """
    return original_article_draft

def get_sentence_level_suggestions() -> str:
    """
    Retrieve the sentence level suggestions.
    
    Returns:
        str: The sentence level suggestions content, or empty string if not set.
    """
    return sentence_level_suggestions

def clear_intermediate_state() -> None:
    """
    Clear all intermediate state variables. This should be called at the start
    of each new workflow execution to prevent data from previous runs.
    """
    global original_article_draft, sentence_level_suggestions
    original_article_draft = ""
    sentence_level_suggestions = ""