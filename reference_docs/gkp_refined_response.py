"""
This is the refined response for the Google Keywords API when you call
gkp = GoogleKeywordsAPI()
gkp.generate_keywords(keywords=["coffee", "tea"]) or gkp.get_static_keywords(keywords=["coffee", "tea"])

We parse the raw response from the Google Keywords API and refine it into a more structured format.
The response is a list of dictionaries, each containing keyword data.

it will look like this (sorted by average monthly searches highest to lowest):
"""

gkp_refined_response = [
    {
        "average_monthly_searches": 13600000,
        "competition": "LOW",
        "competition_index": 9,
        "monthly_search_volumes": {
            "April 2025": 11100000,
            "August 2024": 16600000,
            "December 2024": 13600000,
            "February 2025": 7480000,
            "January 2025": 11100000,
            "July 2024": 16600000,
            "June 2024": 16600000,
            "March 2025": 9140000,
            "May 2024": 13600000,
            "November 2024": 13600000,
            "October 2024": 16600000,
            "September 2024": 16600000,
        },
        "text": "coffee",
    },
    {
        "average_monthly_searches": 550000,
        "competition": "MEDIUM",
        "competition_index": 41,
        "monthly_search_volumes": {
            "April 2025": 550000,
            "August 2024": 550000,
            "December 2024": 823000,
            "February 2025": 450000,
            "January 2025": 673000,
            "July 2024": 550000,
            "June 2024": 550000,
            "March 2025": 550000,
            "May 2024": 673000,
            "November 2024": 673000,
            "October 2024": 673000,
            "September 2024": 550000,
        },
        "text": "tea",
    },
    {
        "average_monthly_searches": 2900,
        "competition": "LOW",
        "competition_index": 5,
        "monthly_search_volumes": {
            "April 2025": 3600,
            "August 2024": 2400,
            "December 2024": 2400,
            "February 2025": 2900,
            "January 2025": 2900,
            "July 2024": 2400,
            "June 2024": 2400,
            "March 2025": 3600,
            "May 2024": 2400,
            "November 2024": 2900,
            "October 2024": 2400,
            "September 2024": 2900,
        },
        "text": "coffee in",
    },
]
