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
# from src.tools.google_keywords_api import GoogleKeywordsAPI
# gkp = GoogleKeywordsAPI()

# async def test_google_keywords_api():
#     keywords = ["upenn graduates", "penn alums", "penn medicine"]
#     results = await gkp.get_static_keywords(keywords=keywords)
#     # results = await gkp.generate_keywords(keywords=keywords)
#     print(f"\n\nTotal keywords found: {len(results)}")
#     print(f"Keywords are: {', '.join([result['text'] for result in results])}")
#     print("Generated Keywords:")
#     for result in results:
#         pprint(result)
#         print("\n")

# asyncio.run(test_google_keywords_api())


##########
# ### Test: Keyword agent workflow
##########
from src.agents.keywords_agent.graph import run_keyword_agent_stream
from src.test_user_input import sample_input, sample_input2

async def test_keyword_agent_workflow():
    await run_keyword_agent_stream(user_input=sample_input2)
    # await run_keyword_agent_stream(user_input=sample_input)

asyncio.run(test_keyword_agent_workflow())

##########
# ### Test: GroqModel
##########
# from src.utils.models_initializer import get_groq_model
# groq_model = get_groq_model()
# messages = [
#     (
#         "system",
#         "You are a geography expert. ",
#     ),
#     ("human", "Tell me an interesting mind boggling fact about Amazon rainforest."),
# ]
# ai_msg = groq_model.invoke(messages)
# print(f"AI message: {ai_msg}")