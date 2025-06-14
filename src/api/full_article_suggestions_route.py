from fastapi import APIRouter
from pydantic import BaseModel
from src.agents.keywords_agent.full_article_generator import suggest_full_article

# Create router with descriptive prefix and tags for API documentation
router = APIRouter(prefix="/agent/suggestfullarticle", tags=["FULL_ARTICLE_SUGGESTION"])


class FullArticleSuggestionResponse(BaseModel):
    """
    Response model for full article suggestion API endpoint.
    
    Attributes:
        success (bool): Indicates if the operation was successful
        article_suggestion (str): The generated full article suggestion content
        message (str): Optional message providing additional context
    """
    success: bool
    article_suggestion: str
    message: str


@router.post("/", response_model=FullArticleSuggestionResponse)
async def generate_full_article_suggestion() -> FullArticleSuggestionResponse:
    """
    Generate a full article suggestion based on previously processed content.
    
    This endpoint calls the suggest_full_article() method to generate a complete
    article suggestion using the original article draft and sentence-level suggestions
    that were processed earlier in the workflow.
      Returns:
        FullArticleSuggestionResponse: Response containing the generated article suggestion
    """
    try:
        # Call the suggest_full_article function to generate the article suggestion
        article_content: str = await suggest_full_article()
        
        # Return successful response with the generated article content
        return FullArticleSuggestionResponse(
            success=True,
            article_suggestion=article_content,
            message="Full article suggestion generated successfully"
        )
        
    except Exception as e:
        # Handle any errors that occur during article generation
        # Return error response with success=False and empty article_suggestion
        return FullArticleSuggestionResponse(
            success=False,
            article_suggestion="",
            message=f"Failed to generate full article suggestion: {str(e)}"
        )