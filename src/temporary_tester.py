"""
Here we test different parts of the code as a scratchpad. To be deleted later.
"""

import asyncio
from pprint import pprint

#####
# ### Test: Exa Web Search async
#####
# from src.tools.web_search_tool import WebSearch


# async def test_exa_web_search():
#     exa_search = WebSearch()
#     exa_search_result = await exa_search._arun(
#         query="best enterprise RAG search engine"
#     )
#     print(exa_search_result)


# asyncio.run(test_exa_web_search())

############
# #### Test : Tavily Web Search async
###########
# async def test_tavily_web_search():
#     tavily_search = WebSearch()
#     tavily_search_result = await tavily_search._arun(query="what percent of penn undergrad students of 2025 found a job?")
#     print(tavily_search_result)

# asyncio.run(test_tavily_web_search())


##############
# ### Test: Google Keywords API
##############
from src.tools.google_keywords_api import GoogleKeywordsAPI
gkp = GoogleKeywordsAPI()

async def test_google_keywords_api():
    keywords = ["upenn graduates", "penn alums", "penn medicine"]
    results = await gkp.get_static_keywords(keywords=keywords)
    # results = await gkp.generate_keywords(keywords=keywords)
    print(f"\n\nTotal keywords found: {len(results)}")
    print(f"Keywords are: {', '.join([result['text'] for result in results])}")
    print("Generated Keywords:")
    for result in results:
        pprint(result)
        print("\n")

asyncio.run(test_google_keywords_api())
