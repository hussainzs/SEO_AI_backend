from typing import Any, Literal, Optional

from src.utils.models_initializer import get_tavily_client, get_exa_client
from pydantic import BaseModel, Field
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from langchain_core.tools.base import ArgsSchema

# For now we choose manually whether to use Tavily or Exa, later we will use a rate limiter to switch between them based on usage patterns
"""
Tavily Docs: https://docs.tavily.com/sdk/python/reference#tavily-search

Exa Docs: https://docs.exa.ai/sdks/python-sdk-specification#search-and-contents-method
"""
chat_client: Literal["tavily", "exa"] = "exa"

# NOTE: refer to `reference_docs/web_search_responses.txt` for expected raw response from Tavily and Exa and parsed refined responses.

# some other constants we will feed into our tavily or exa client
web_search_params = {
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
    },
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
        "The result contains a 'score' which is a relevance score of the search result to the query."
        "The tool result also contains highlights which are snippets of the content from each url that are relevant to the query."
    )
    args_schema: Optional[ArgsSchema] = WebSearchToolSchema

    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """
        Run the web search tool with the given query.
        """
        search_params = {}
        if chat_client == "tavily":
            search_params = web_search_params["tavily"]
            client = get_tavily_client()
            response = client.search(query=query, **search_params)  # type: ignore
            response = self._parse_tavily_response(response)  # type: ignore
        else:
            search_params = web_search_params["exa"]
            client = get_exa_client()
            response = client.search_and_contents(
                query=query, **search_params  # type: ignore
            )
            response = self._parse_exa_response(response)

        return response

    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """
        Asynchronously run the web search tool with the given query.
        """
        search_params = {}
        if chat_client == "tavily":
            client = get_tavily_client(return_async=True)
            response = await client.search(
                query=query, **web_search_params["tavily"]  # type: ignore
            )
            response = self._parse_tavily_response(response)
        else:
            client = get_exa_client(return_async=True)
            response = await client.search_and_contents(
                query=query, **web_search_params["exa"]  # type: ignore
            )
            response = self._parse_exa_response(response)

        return response

    def _parse_exa_response(self, response_obj: Any) -> str:
        """Parses the Exa API response object to extract only relevant fields.

        This function extracts the 'title', 'score', 'published date', 'author', and 'highlights'
        from each result in the Exa API response. It returns a string representation of a list of
        dictionaries, each containing only these fields.

        Args:
            response_obj (Any): The response object returned by the Exa API. It is expected to be a
                dictionary with a 'results' key containing a list of result items.

        Returns:
            str: A string representation of a list of dictionaries, each with the selected fields.

        Raises:
            KeyError: If the expected 'results' key is missing in the response object.
            Exception: For any other unexpected errors during parsing.
        """
        try:
            parsed_results = []

            # Response object is a SearchResponse object has an attribute 'results' which is a list of Result objects
            # we iterate through the list, grab each Result object and extract the relevant fields
            for item in response_obj.results:
                parsed_item = {
                    "title": item.title,
                    "url": item.url,
                    "score": item.highlight_scores,
                    "published_date": item.published_date,
                    "author": item.author,
                    "highlights": item.highlights,
                }
                parsed_results.append(parsed_item)

            return str(parsed_results)

        except KeyError as key_err:
            raise KeyError(
                f"Missing expected key in Exa response: {key_err}"
            ) from key_err
        except Exception as exc:
            raise Exception(f"Failed to parse Exa response: {exc}") from exc

    def _parse_tavily_response(self, response_obj: dict[str, Any]) -> str:
        """Parses the Tavily API response object to extract only relevant fields.

        This function extracts the 'url', 'title', 'score', 'published_date', and 'content'
        (renamed to 'highlights') from each result in the Tavily API response. It returns a string
        representation of a list of dictionaries, each containing only these fields.

        Args:
            response_obj (dict[str, Any]): The response object returned by the Tavily API. It is expected to be a
                dictionary with a 'results' key containing a list of result items.

        Returns:
            str: A string representation of a list of dictionaries, each with the selected fields.

        Raises:
            KeyError: If the expected 'results' key is missing in the response object.
            ValueError: If the 'results' field is not a list.
        """
        try:
            # Initialize an empty list to store the parsed results
            parsed_results: list[dict[str, Optional[Any]]] = []

            # Attempt to retrieve the list of results from the response object
            results: list[dict[str, Any]] = response_obj.get("results", [])
            if not isinstance(results, list):
                raise ValueError("The 'results' field is not a list.")

            # Iterate over each result and extract only the required fields, renaming 'content' to 'highlights'
            for item in results:
                parsed_item: dict[str, Optional[Any]] = {
                    "url": item.get("url"),
                    "title": item.get("title"),
                    "score": item.get("score"),
                    "published_date": item.get("published_date"),
                    "highlights": item.get("content"),
                }
                parsed_results.append(parsed_item)

            # Convert the list of dictionaries to a string and return
            return str(parsed_results)

        except KeyError as key_err:
            # Raise a KeyError if the expected key is missing
            raise KeyError(
                f"Missing expected key in tavily response: {key_err}"
            ) from key_err
        except ValueError as val_err:
            # Raise a ValueError if the results field is not a list
            raise ValueError(
                f"Invalid format in Tavily response, results field is not a list: {val_err}"
            ) from val_err
        except Exception as exc:
            # Raise any other exceptions that occur during parsing
            raise Exception(f"Failed to parse Tavily response: {exc}") from exc
