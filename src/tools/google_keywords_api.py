import os
from typing import Any
import httpx  # Use httpx for async HTTP requests
from httpx import Response, RequestError, TimeoutException, ConnectError

# Get base url from environment variable
BASE_URL = os.getenv("GKP_URL", "")

class GoogleKeywordsAPI:
    """
    A client for interacting with the Google Ads Keywords Microservice API.

    This class provides methods to generate keyword ideas, retrieve static test data,
    and check the API status.

    Attributes:
        base_url: The base URL of the Google Keywords API.
        timeout: The timeout for API requests in seconds.
    """

    def __init__(self, base_url: str = BASE_URL, timeout: int = 45) -> None:
        """
        Initialize the Google Keywords API client.

        Args:
            base_url: The base URL of the API. Defaults to the value of the GKP_URL environment variable.
            timeout: The timeout for API requests in seconds. Defaults to 45.
        """
        self.base_url = base_url
        self.timeout = timeout

    async def check_api_status(self) -> dict[str, str]:
        """
        Check if the Google Keywords API is running.

        Returns:
            A dictionary containing the API status message.

        Raises:
            ConnectError: If the API is not reachable.
            RequestError: If any other error occurs during the request.

        Example:
            >>> api = GoogleKeywordsAPI()
            >>> await api.check_api_status()
            {'message': 'Google Ads Keyword Microservice is running'}
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response: Response = await client.get(
                    url=f"{self.base_url}/"
                )
                response.raise_for_status()
                return response.json()
            except ConnectError:
                raise ConnectError("Google Keywords API is not reachable")
            except RequestError as e:
                raise

    async def generate_keywords(
        self,
        keywords: list[str],
        url: str = "https://www.thedp.com/",
        location_id: str = "2840",
        language_id: str = "1000"
    ) -> list[dict[str, Any]]:
        """
        Generate keyword ideas using the Google Keywords API.

        Args:
            keywords: A non-empty list of keyword strings to use as seeds.
            url: The URL to use as a seed. Defaults to "https://www.thedp.com/".
            location_id: The location ID string. Defaults to "2840" (USA).
            language_id: The language ID string. Defaults to "1000" (English).

        Returns:
            A list of dictionaries containing keyword data, sorted by average monthly searches.

        Raises:
            ValueError: If the keywords list is empty.
            ConnectError: If the API is not reachable.
            RequestError: If any other error occurs during the request.

        Example:
            >>> api = GoogleKeywordsAPI()
            >>> results = await api.generate_keywords(keywords=["coffee", "tea"])
            >>> print(results[0]["text"])
            'coffee'
        """
        return await self._execute_keyword_request(
            endpoint="/keywords/generate",
            keywords=keywords,
            url=url,
            location_id=location_id,
            language_id=language_id
        )

    async def get_static_keywords(
        self,
        keywords: list[str],
        url: str = "https://www.thedp.com/",
        location_id: str = "2840",
        language_id: str = "1000"
    ) -> list[dict[str, Any]]:
        """
        Get static test keyword ideas from the Google Keywords API.

        This method is useful for testing without consuming actual API credits.

        Args:
            keywords: A non-empty list of keyword strings to use as seeds.
            url: The URL to use as a seed. Defaults to "https://www.thedp.com/".
            location_id: The location ID string. Defaults to "2840" (USA).
            language_id: The language ID string. Defaults to "1000" (English).

        Returns:
            A list of dictionaries containing keyword data, sorted by average monthly searches.

        Raises:
            ValueError: If the keywords list is empty.
            ConnectError: If the API is not reachable.
            RequestError: If any other error occurs during the request.

        Example:
            >>> api = GoogleKeywordsAPI()
            >>> results = await api.get_static_keywords(keywords=["coffee", "tea"])
            >>> print(results[0]["text"])
            'coffee'
        """
        return await self._execute_keyword_request(
            endpoint="/keywords/static",
            keywords=keywords,
            url=url,
            location_id=location_id,
            language_id=language_id
        )

    async def _execute_keyword_request(
        self,
        endpoint: str,
        keywords: list[str],
        url: str,
        location_id: str,
        language_id: str
    ) -> list[dict[str, Any]]:
        """
        Internal method to make a request to the keyword endpoints.

        Args:
            endpoint: The API endpoint to call.
            keywords: A non-empty list of keyword strings to use as seeds.
            url: The URL to use as a seed.
            location_id: The location ID string.
            language_id: The language ID string.

        Returns:
            A list of dictionaries containing keyword data, sorted by average monthly searches.

        Raises:
            ValueError: If the keywords list is empty.
            ConnectError: If the API is not reachable.
            RequestError: If any other error occurs during the request.
        """
        # Validate input parameters
        if not keywords:
            raise ValueError("Keywords list cannot be empty")

        payload = {
            "keywords": keywords,
            "url": url,
            "location_id": location_id,
            "language_id": language_id
        }

        # Use async HTTP client to make POST request
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response: Response = await client.post(
                    url=f"{self.base_url}{endpoint}",
                    json=payload
                )
                response.raise_for_status()
                # Parse and transform the response
                return await self._parse_keywords_response(response.json())
            except ConnectError:
                raise ConnectError(f"Google Keywords API is not reachable at {endpoint}")
            except TimeoutException:
                raise TimeoutException(f"Request to {endpoint} timed out after {self.timeout} seconds")
            except RequestError as e:
                raise

    async def _parse_keywords_response(self, response_data: dict[str, Any]) -> list[dict[str, int | str | dict[str, int]]]:
        """
        Parse and transform the API response into a simplified format.
        Reference to `reference_docs/gkp_raw_sample_response.json` to understand the input to this method.
        Reference to `reference_docs/gkp_refined_response.json` to understand the output of this method.

        Args:
            response_data: The raw API response data.

        Returns:
            A list of dictionaries containing simplified keyword data, sorted by 
            average monthly searches (highest to lowest) and limited to top 25 results.
        """
        results = []
        # Process each keyword in the results
        for keyword_data in response_data.get("results", []):
            keyword_text = keyword_data.get("text", "")
            metrics = keyword_data.get("keyword_idea_metrics", {})
            
            # Format monthly search volumes
            monthly_volumes = {}
            for volume in metrics.get("monthly_search_volumes", []):
                month = volume.get("month", "").capitalize()
                year = volume.get("year", "")
                searches = volume.get("monthly_searches", "0")
                # Format as "Month Year": searches
                date_key = f"{month} {year}"
                monthly_volumes[date_key] = int(searches)
                
            # Create simplified keyword object
            keyword_obj = {
                "text": keyword_text,
                "competition": metrics.get("competition", ""),
                "average_monthly_searches": int(metrics.get("avg_monthly_searches", "0")),
                "competition_index": int(metrics.get("competition_index", "0")),
                "monthly_search_volumes": monthly_volumes
            }
            
            results.append(keyword_obj)
            
        # Sort by average_monthly_searches (highest to lowest)
        results.sort(key=lambda x: x["average_monthly_searches"], reverse=True)
        
        # Limit to top 25 results
        return results[:25]
