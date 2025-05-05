"""
Here we will create a simple langGraph workflow with one tool and get streaming output which will be sent to FastAPI.
We need to use async.
"""

import os
from json import dumps as json_dump
from typing import Any, Literal, Optional
from dotenv import load_dotenv
from langgraph.graph import MessagesState

# For defining custom Tools
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from langchain_core.tools.base import ArgsSchema
from pydantic import BaseModel, Field

from tavily import (
    TavilyClient,
    AsyncTavilyClient,
)  # provides us the TavilyClient class to interact with the Tavily API

# *******************Pre Work*******************

# Load the environment variables from the .env file
load_dotenv()

# Define the Tavily client for the web search tool.
tavily_api_key: str | None = os.getenv("TAVILY_API_KEY")
if not tavily_api_key:
    raise ValueError(
        "TAVILY_API_KEY environment variable not set."
    )  # In real application, we would do this validation in a separate file.

tavily_client = TavilyClient(api_key=tavily_api_key)
async_tavily_client = AsyncTavilyClient(api_key=tavily_api_key)


# Define the state of the graph
class State(MessagesState):
    """
    Remember: Subclassing MessageState by LangGraph provides us with a `messages` state automatically with the right reducer.
    """

    num_of_steps: int


# Now lets define the TOOLS we will use in the graph. We define our tool by subclassing BaseTool
# 1. First define the input schema for the tool. This is a simple pydantic model that defines the input parameters for the tool.
class WebSearchToolSchema(BaseModel):
    query: str = Field(
        ...,
        description="The query to search the web for. Formulate this optimized for finding information on the web related to what user needs.",
    )
    topic: Literal["news", "general"] = Field(
        default="general",
        description="The topic to search for. Can be either 'news' or 'general'.",
    )


# 2. Now we define the tool itself. We subclass BaseTool and define the name, description and args_schema.
# We then define the _run method which will be called when the tool is executed. The _run method takes the input parameters and calls the Tavily API to get the search results.
# Note: It's important that every field has type hints. BaseTool is a Pydantic class and not having type hints can lead to unexpected behavior.
class Web_Search_Tool(BaseTool):
    name: str = "web_search_tool"
    description: str = (
        "Use this tool to search the internet for latest information or any specific information about a topic. If you are asked about news always use this tool with topic 'news'. Your query should be concise (strictly less than 300 characters). The output will include an LLM generated answer. Evaluate the answer and if it is not correct, use the web search results to generate a new answer. The output also includes a relevancy score for each source. Higher score means generally more relevant."
    )
    args_schema: Optional[ArgsSchema] = WebSearchToolSchema

    def _run(
        self,
        query: str,
        topic: Literal["news", "general"] = "general",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        # Now using LLM generated parameters and some hardcoded ones we will call the Tavily API
        response = tavily_client.search(
            query=query, topic=topic, max_results=2, include_answer=True
        )
        return json_dump(
            response
        )  # convert the response to a json string as the LLMs expect a string from the tool.

    async def _arun(
        self,
        query: str,
        topic: Literal["news", "general"] = "general",
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        try:
            # Perform the asynchronous search with the same parameters as the sync version
            response = await async_tavily_client.search(
                query=query, topic=topic, max_results=2, include_answer=True
            )
            return json_dump(response)  # Convert the response to a JSON string
        except Exception as e:
            # Proper error handling with meaningful message
            error_message = f"Asynchronous web search failed: {str(e)}"
            if run_manager:
                await run_manager.on_tool_error(error=e)
            raise RuntimeError(error_message)
