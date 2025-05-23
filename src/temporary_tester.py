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
# from src.agents.keywords_agent.graph import run_keyword_agent_stream
# from src.test_user_input import sample_input, sample_input2

# async def test_keyword_agent_workflow():
#     await run_keyword_agent_stream(user_input=sample_input2)
#     # await run_keyword_agent_stream(user_input=sample_input)

# asyncio.run(test_keyword_agent_workflow())

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

##############
# ### Test: MistralModel and OpenAI with tools and structured output
##############
from langchain_mistralai import ChatMistralAI
from langchain_openai import ChatOpenAI
from src.utils.settings import settings
from src.tools.web_search_tool import dummy_web_search_tool
from pydantic import BaseModel, Field

class WebSearchResult(BaseModel):
    """Individual web search result with structured fields."""
    rank: int = Field(
        ...,
        description="The ranking position of this search result"
    )
    title: str = Field(
        ...,
        description="The title of the web page"
    )
    url: str = Field(
        ...,
        description="The URL of the web page",
    )

class StructuredOutputModel(BaseModel):
    """Structured output model for search query generation and analysis."""
    generated_search_queries: list[str] = Field(
        ...,
        description="List of 2 generated search queries that will answer the user query",
    )
    web_search_results: list[WebSearchResult] = Field(
        ...,
        description="List of web search results you would expect to get from the web search tool",
    )
    analysis: str = Field(
        ...,
        description="A 2 sentence analysis of why these search results are relevant to the user query"
    )

# Initialize OpenAI LLM with structured output using the updated schema
# openai_llm = ChatOpenAI(
#     model="gpt-4o-mini",  # Changed to supported model for json_schema method
#     temperature=0.5,
#     timeout=None,
#     max_retries=2,
#     api_key=settings.OPENAI_API_KEY,
# )
# # openai_llm = openai_llm.bind_tools([dummy_web_search_tool])

# # Use structured output with strict mode enabled for better validation
# openai_llm = openai_llm.with_structured_output(
#     schema=StructuredOutputModel,
#     method="json_schema",  # Explicitly use json_schema method
#     strict=True  # Enable strict validation
# )

messages = [
    (
        "system",
        # "You are a helpful assistant and answers about world politics in 2 sentences maximum."
        # "You are given a web search tool. make a web search tool call with the query to get the answer user asks for",
        "You have to understand user query, generate 2 unique search queries that will answer the user query, come up with fictitious web search results and provide a 2 sentence analysis of why these search results are relevant to the user query. Answer in the structured format provided to you.",
    ),
    ("human", "How is AI changing the world politics?"),
]

# ai_msg = openai_llm.invoke(messages)
# print(f"{ai_msg}")

#-------------------------------------------------------------------------------
mistral_llm = ChatMistralAI(
    model_name="mistral-medium-2505",
    temperature=0.5,
    max_retries=2,
    api_key=settings.MISTRAL_API_KEY
)
# mistral_llm = mistral_llm.bind_tools([dummy_web_search_tool])

# Use structured output with strict mode enabled for better validation
mistral_llm = mistral_llm.with_structured_output(
    schema=StructuredOutputModel,
    method="json_schema",  # Explicitly use json_schema method
    strict=True  # Enable strict validation
)
ai_message = mistral_llm.invoke(messages)
print(f"{ai_message}")