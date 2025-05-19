"""
Here we test different parts of the code as a scratchpad. To be deleted later.
"""
import asyncio

#####
# ### Test: Exa Web Search async
#####
from src.tools.web_search_tool import WebSearch

async def test_exa_web_search():
    exa_search = WebSearch()
    exa_search_result = await exa_search._arun(query="best enterprise RAG search engine")
    print(exa_search_result)
    
asyncio.run(test_exa_web_search())

############
# #### Test : Tavily Web Search async
###########
# async def test_tavily_web_search():
#     tavily_search = WebSearch()
#     tavily_search_result = await tavily_search._arun(query="what percent of penn undergrad students of 2025 found a job?")
#     print(tavily_search_result)

# asyncio.run(test_tavily_web_search())