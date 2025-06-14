original_article_draft: str = ""
sentence_level_suggestions: str = ""

def set_original_article_draft(draft: str) -> None:
    """
    Set the original article draft.
    
    Args:
        draft (str): The original article draft.
    """
    global original_article_draft
    original_article_draft = draft
    
def set_sentence_level_suggestions(suggestions: str) -> None:
    """
    Set the sentence level suggestions.
    
    Args:
        suggestions (str): The sentence level suggestions.
    """
    global sentence_level_suggestions
    sentence_level_suggestions = suggestions
