from typing import Any, Literal, Optional

from src.utils.models_initializer import get_tavily_client, get_exa_client
from pydantic import BaseModel, Field
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from langchain_core.tools.base import ArgsSchema
from langchain_core.tools import tool

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
                    "url": item.url,
                    "title": item.title,
                    "score": item.highlight_scores,
                    "published_date": item.published_date,
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


# Create a dummy web search tool for testing
@tool
def dummy_web_search_tool(query: str) -> str:
    """
    Dummy web search tool that returns a hardcoded response.
    This is used for testing purposes only.

    Args:
        query (str): The search query to execute.
    """
    return str(
        [
            {
                "url": "https://www.cnbc.com/2025/05/16/how-college-grads-can-find-a-job-in-a-tough-market.html",
                "title": "College grads face a 'tough and competitive' job market this year, expert says - CNBC",
                "score": 0.2830381,
                "published_date": "Fri, 16 May 2025 10:40:01 GMT",
                "highlights": 'A majority, 62%, of the Class of 2025 are concerned about what AI will mean for their jobs, compared to 44% two years ago, according to a survey by Handshake.',
            },
            {
                "url": "https://www.hrdive.com/news/2025-raises-lower-than-expected/747142/",
                "title": "2025 raises fell short of employers’ recent projections, Mercer finds - HR Dive",
                "score": 0.19355896,
                "published_date": "Mon, 05 May 2025 21:00:53 GMT",
                "highlights": "Pay expectations for recent graduates aren’t being met either, according to an April ZipRecruiter report. About 42% of recent graduates said they didn’t get the pay they wanted in their job search.",
            },
            {
                "url": "https://www.post-gazette.com/news/education/2025/05/13/penn-state-campus-closures-fayette-new-kensington-shenango/stories/202505130066",
                "title": "Penn State proposes 7 campus closures, including 3 in Pittsburgh region - Pittsburgh Post-Gazette",
                "score": 0.12024263,
                "published_date": "Tue, 13 May 2025 20:21:41 GMT",
                "highlights": "Enrollment drops at the commonwealth campuses have been a yearslong struggle. At Western Pennsylvania campuses between fall 2020 and fall 2024, student declines have varied from 7% (Penn State Behrend in Erie) to 29% (Penn State Fayette).",
            },
            {
                "url": "https://www.post-gazette.com/sports/paul-zeise/2025/05/12/aaron-rodgers-nevillewood-steelers-offseason/stories/202505120061",
                "title": "Paul Zeise: Aaron Rodgers may or may not join a local country club, but he made this Steelers offseason entertaining - Pittsburgh Post-Gazette",
                "score": 0.094719745,
                "published_date": "Mon, 12 May 2025 23:38:05 GMT",
                "highlights": "1 news Penn State pushes back against report detailing possible campus closures Mon, May 12, 2025, 11:50pm Megan Tomasic 2 sports Paul Zeise: Aaron Rodgers may or may not join a local country club, but he made this Steelers offseason entertaining Mon, May 12, 2025, 11:38pm Paul Zeise 3 sports Instant analysis: Pirates lose to Mets on Pete Alonso sacrifice fly Tue, May 13, 2025, 2:14am Colin Beazley 4 business Student debt will follow him to the grave — and he still makes payments Mon, May 12.",
            },
            {
                "url": "https://www.post-gazette.com/sports/pirates/2025/05/14/pirates-mets-bryan-reynolds-mitch-keller-loss/stories/202505130046",
                "title": "3 takeaways: Pirates have a Bryan Reynolds problem right now - Pittsburgh Post-Gazette",
                "score": 0.08716692,
                "published_date": "Wed, 14 May 2025 04:19:22 GMT",
                "highlights": "1 news Pittsburgh International Airport's new terminal is nearly complete Wed, May 14, 2025, 12:33am.",
            },
        ]
    )
