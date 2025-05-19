from typing import Literal, Optional
from src.utils.models_initializer import get_tavily_client, get_exa_client
from pydantic import BaseModel, Field
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from langchain_core.tools.base import ArgsSchema

# For now we choose manually whether to use Tavily or Exa, later we will use a rate limiter to switch between them based on usage patterns
chat_client: Literal["tavily", "exa"] = "exa"

# some other constants we will feed into our tavily or exa client
web_search_params: dict[str, dict[str, str | bool | int]] = {
    "tavily": {
        "search_depth": "advanced",
        "topic": "news",
        # default is 7 days, but we may have to change this later as this should depend on input. 
        "days": 14,
        "max_results": 5,
        "chunks_per_source": 3,
        # since our purpose is to do competitor analysis, we dont need LLM generated answer to our search query
        "include_answer": False,
    },
    "exa": {
        "highlights": True,
        "num_results": 5,
        "type": "keyword",
        "category": "news",
        
    }
}

class WebSearchToolSchema(BaseModel):
    query: str = Field(
        ...,
        description="The query to search the web for",
    )

class WebSearch(BaseTool):
    name: str = "web_search_tool"
    description: str = (
        f"Conducts a web search using {chat_client} API for the given query. Keep the 'query' concise (under 300 characters)."
    )
    args_schema: Optional[ArgsSchema] = WebSearchToolSchema