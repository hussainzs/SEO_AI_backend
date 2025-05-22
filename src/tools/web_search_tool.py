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
                "highlights": 'A majority, 62%, of the Class of 2025 are concerned about what AI will mean for their jobs, compared to 44% two years ago, according to a survey by Handshake. Graduates in the humanities and computer science are the most worried about AI\'s impact on jobs.\n"I think it\'s more about a redefinition of the entry level than it is about an elimination of the entry level," Cruzvergara said. [...] "In early January, the class of 2025 was on track to meet and even exceed the number of applications to federal government jobs," Cruzvergara said. When the executive orders hit in mid-January there was\xa0 "a pretty steep decline all of a sudden, she said.\n"The federal government is one of the largest employers in this country, and also one of the largest employers for entry-level employees as well," said Loujaina Abdelwahed, senior economist at Revelio Labs, a workforce intelligence firm. [...] College grads face a \'tough and competitive\' job market this year, expert says\nNew college graduates looking for work now are finding a tighter labor market than they expected even a few months ago.\nThe unemployment rate for recent college grads reached 5.8% in March, up from 4.6% the same time a year ago, according to an April report from the Federal Reserve Bank of New York.',
            },
            {
                "url": "https://www.hrdive.com/news/2025-raises-lower-than-expected/747142/",
                "title": "2025 raises fell short of employers’ recent projections, Mercer finds - HR Dive",
                "score": 0.19355896,
                "published_date": "Mon, 05 May 2025 21:00:53 GMT",
                "highlights": "Pay expectations for recent graduates aren’t being met either, according to an April ZipRecruiter report. About 42% of recent graduates said they didn’t get the pay they wanted in their job search. And soon-to-be graduates said they expected to earn $101,500 on average, while the average starting salary among recent graduates was $68,400, ZipRecruiter found.\npurchase licensing rights\nFiled Under: Comp & Benefits\nHR Dive news delivered to your inbox [...] In the survey of more than 800 U.S. companies, employers said they expected to promote about 10% of their workforce, up from 8% the previous year, and to award an average raise of 8.5% with promotions.\nAmong the 44% of companies that rely on a five-tier performance rating system, top performers received average raises of 5.6%, while those who fell in the middle on performance earned 3.3%, Mercer said. [...] By signing up to receive our newsletter, you agree to our Terms of Use and Privacy Policy. You can unsubscribe at anytime.\nSign up A valid email address is required. Please select at least one newsletter.",
            },
            {
                "url": "https://www.post-gazette.com/news/education/2025/05/13/penn-state-campus-closures-fayette-new-kensington-shenango/stories/202505130066",
                "title": "Penn State proposes 7 campus closures, including 3 in Pittsburgh region - Pittsburgh Post-Gazette",
                "score": 0.12024263,
                "published_date": "Tue, 13 May 2025 20:21:41 GMT",
                "highlights": "Enrollment drops at the commonwealth campuses have been a yearslong struggle. At Western Pennsylvania campuses between fall 2020 and fall 2024, student declines have varied from 7% (Penn State Behrend in Erie) to 29% (Penn State Fayette).\nThese enrollment challenges are exacerbated by a looming demographic cliff that will particularly impact the Northeast and Midwest. The Keystone State’s share of high school graduates is expected to drop 17% by 2041. [...] Published Time: 2025-05-13T13:01:06-04:00\nPenn State proposes 7 campus closures, including 3 in Pittsburgh region | Pittsburgh Post-Gazette\nTuesday, May 13, 2025, 8:41PM\xa0|\xa0 67°\nObituaries\nPGe\nPG Store\nArchives\nClassifieds\nClassified\nEvents\nJobs\nPublic Notices\nPets\nMENU\nSUBSCRIBE\nLOGIN\nREGISTER\nLOG OUT\nMY PROFILE\nHome\nNews\nLocal\nSports\nOpinion\nA&E\nLife\nBusiness\nContact Us\nNEWSLETTERS\nSenate committee rejects bill that would have legalized recreational pot in Pa. [...] The past year has seen Penn State already take significant steps to reduce costs at the branch campuses. School officials cut $49 million from the commonwealth campuses’ 2025-26 budget, dropping it to $340 million, and they announced in February that they plan to trim an additional $25 million from the campuses in 2026-27.\nLast summer, Penn State officials also offered a buyout accepted by two in 10 eligible faculty and staff, and combined leadership at 11 campuses.\nOngoing battle",
            },
            {
                "url": "https://www.post-gazette.com/sports/paul-zeise/2025/05/12/aaron-rodgers-nevillewood-steelers-offseason/stories/202505120061",
                "title": "Paul Zeise: Aaron Rodgers may or may not join a local country club, but he made this Steelers offseason entertaining - Pittsburgh Post-Gazette",
                "score": 0.094719745,
                "published_date": "Mon, 12 May 2025 23:38:05 GMT",
                "highlights": "1 news Penn State pushes back against report detailing possible campus closures Mon, May 12, 2025, 11:50pm Megan Tomasic 2 sports Paul Zeise: Aaron Rodgers may or may not join a local country club, but he made this Steelers offseason entertaining Mon, May 12, 2025, 11:38pm Paul Zeise 3 sports Instant analysis: Pirates lose to Mets on Pete Alonso sacrifice fly Tue, May 13, 2025, 2:14am Colin Beazley 4 business Student debt will follow him to the grave — and he still makes payments Mon, May 12, [...] Education\nHealth & Wellness\nTransportation\nState\nNation\nWorld\nWeather News\nObituaries\nNews Obituaries\nScience\nEnvironment\nFaith & Religion\nSocial Services\nLOCAL\nLocal Home\nCity\nRegion\nEast\nNorth\nSouth\nWest\nWashington\nWestmoreland\nObituaries\nClassifieds\nPublic Notices\nSPORTS\nSports Home\nSteelers\nPenguins\nPirates\n2025 U.S. Open\nSports Columns\nGene Collier\nJason Mackey\nJoe Starkey\nPaul Zeise\nPitt\nPenn State\nWVU\nNorth Shore Drive Podcast\nRiverhounds\nParis 2024 Olympics\nSports Betting [...] Random Acts of Kindness\nSeen\nOutdoors\nStyle & Fashion\nTravel\nHolidays\nDow leaps 1,100 points and S&P 500 rallies 3.3% following a 90-day truce in the U.S.-China trade war\nTrump signs executive order setting 30-day deadline for drugmakers to lower prescription drug costs\nStudent debt will follow him to the grave — and he still makes payments\nPennsylvania’s broadband expansion plans stall amid federal delays\nWith 346 days to go, the 2026 NFL draft countdown clock debuts on the North Shore",
            },
            {
                "url": "https://www.post-gazette.com/sports/pirates/2025/05/14/pirates-mets-bryan-reynolds-mitch-keller-loss/stories/202505130046",
                "title": "3 takeaways: Pirates have a Bryan Reynolds problem right now - Pittsburgh Post-Gazette",
                "score": 0.08716692,
                "published_date": "Wed, 14 May 2025 04:19:22 GMT",
                "highlights": "1 news Pittsburgh International Airport's new terminal is nearly complete Wed, May 14, 2025, 12:33am Adam Babetski 2 news Senate committee rejects bill that would have legalized recreational pot in Pa. Tue, May 13, 2025, 3:53pm Ford Turner 3 sports 3 takeaways: Pirates have a Bryan Reynolds problem right now Wed, May 14, 2025, 4:19am Colin Beazley 4 news Penn State proposes 7 campus closures, including 3 in Pittsburgh region Tue, May 13, 2025, 5:01pm Megan Tomasic and Stephana Ocneanu 5 [...] RSS Feeds\nNEWS\nNews Home\nCrimes & Courts\nPolitics\nEducation\nHealth & Wellness\nTransportation\nState\nNation\nWorld\nWeather News\nObituaries\nNews Obituaries\nScience\nEnvironment\nFaith & Religion\nSocial Services\nLOCAL\nLocal Home\nCity\nRegion\nEast\nNorth\nSouth\nWest\nWashington\nWestmoreland\nObituaries\nClassifieds\nPublic Notices\nSPORTS\nSports Home\nSteelers\nPenguins\nPirates\n2025 U.S. Open\nSports Columns\nGene Collier\nJason Mackey\nJoe Starkey\nPaul Zeise\nPitt\nPenn State\nWVU\nNorth Shore Drive Podcast\nRiverhounds",
            },
        ]
    )
