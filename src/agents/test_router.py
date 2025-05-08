
"""
We will create an routing agent that is capable of answering queries related to the on-going world events, Travel information, Travel restrictions and
get streaming output which will be sent to FASTAPI.

As we will be sending streaming output, we will be using async.

"""

# Environment Setup 
# State Definition 
# Web Search Tool
# Prompt Setup
# Assistant Node 
# Routing logic
# Graph Building
# Streaming Output


print("\n=== Let's start building LangGraph Routing Workflow ===\n")

import os 
from dotenv import load_dotenv
import json 
from json import dumps as json_dump
from pprint import pprint
from typing import Literal, Optional
from IPython.display import display, Image
from langgraph.graph import StateGraph, MessagesState, START, END

# Libraries for custom tools 

from langgraph.graph.state import CompiledStateGraph 
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.callbacks import (

    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun
)

from langchain_core.tools import BaseTool
from langchain_core.tools.base import ArgsSchema 
from pydantic import BaseModel, Field

# Travily Client 
from tavily import(

    TavilyClient,
    AsyncTavilyClient,

) # Allows us to interact with Tavily API


# LLMs 
from langchain_google_genai import ChatGoogleGenerativeAI

# For Prompts
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

# For date time 
from datetime import datetime


print("\n=== Loading Environment Variables and Initializing Clients ===\n")

# Getting environment variables from .env file

load_dotenv()

# Defining Tavily Client for web search tool

tavily_api_key: str | None = os.getenv("TAVILY_API_KEY")
if not tavily_api_key:
    raise ValueError(
        "TAVILY_API_KEY environment variable is not set"

    )
else:
    print("Tavily API Key loaded successfully!")   # Better to confirm if API gets loaded or not!

tavily_client = TavilyClient(api_key=tavily_api_key)
async_tavily_client = AsyncTavilyClient(api_key=tavily_api_key)


# Defining Gemini LLM Client 

def load_gemini_client() -> ChatGoogleGenerativeAI:

    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
    else:
        print(" Gemini API Key loaded successfully!")


    gemini_llm = ChatGoogleGenerativeAI(
        # define model
        model = "gemini-1.5-pro",
        temperature = 0.2, # output varies for same input
        max_tokens = 1000,
        google_api_key = gemini_api_key,
        max_retries = 2,  # retries if request fails due to API or other reasons.
        timeout = 300

    )
    return gemini_llm


# Let's define schema for the structure of Router llm output 

print("\n=== Defining schema the structure of Router output ===\n")

class Route(BaseModel):
    llm_choice: Literal["Time", "Places", "Airlines"] = Field(
        None, description= "Next step in routing workflow"
    )

gemini_llm = load_gemini_client()

router = gemini_llm.with_structured_output(Route)

# Define Class for the graph 
"""
As we are using with_structured_output then we will use MessageState - And also because
we want agent to maintain conversation history, and it is suitable for streaming response!
"""
class State(MessagesState):
    user_input: str
    decision: str
    llm_final_answer: str 

# Let's define the Schema for the tool parameters 

class websearchschema(BaseModel):
    query: str = Field(
        ...,
        description= "This is the query to search the web for. Write it in clear way to get accurate results!"
    )

# Let's define the tool itself. It will be the subclass BaseTool 

class websearch(BaseTool):
    name: str = "web_search_tool"
    description: str = (

        "Searches the internet using Tavily API for up-to-date informatiuon or specific details on a 'query'. "
        "Provides search results, potentially including a summarized answer and source relevancy scores."
        "Keep the 'query' concise (under 300 characters) "
    )

    args_schema: Optional[ArgsSchema] = websearchschema

    def _run(
            
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None   # To handle waiting during asyncronous actions showing the progrss on task continously!

    ) -> str:
        
        print("\n=== executing the search tool=== \n")

        response = tavily_client.search(
        
        query=query, max_results= 2, include_answer=True

    )
        print("Web search completed successfully")
        return json_dump(
            response
    )


    async def _arun(
            
        self,
        query: str, 
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str: 

        try: 

            response = await async_tavily_client.search(

                query=query, max_results=2, include_answer=True
            )

            return json_dump(
                response
            )
        except Exception as e:

            error_message = f"Asynchronous web search failed: {str(e)}"
            print(f"✗ Error: {error_message}")
            if run_manager:
                await run_manager.on_tool_error(error=e)
            raise RuntimeError(error_message)

def get_tools() -> list[BaseTool]:
    "returns list of tool"

    return [websearch()]

def get_model_with_tools():
    "lets bind tools with LLM"

    # load and bind tools to LLM

    gemini_llm: ChatGoogleGenerativeAI = load_gemini_client()

    gemini_llm_with_tools =  gemini_llm.bind_tools(tools=get_tools())

    return gemini_llm_with_tools


# let's create the router llm 

async def llm_call_router(state: State):

    decision = await router.ainvoke([

        SystemMessage(
            content = "Route the input to Time, Places, or Airline on the user's request"
        ),
        HumanMessage(content=state["user_input"])]

    )

    return {"decision": decision.llm_choice}

gemini_llm_with_tools = get_model_with_tools()


# Let's create the Specialized LLM for "Time related queries"

# Let's define Time information expert LLM
async def llm_Time(state:State):
    response = await gemini_llm_with_tools.ainvoke([
        SystemMessage(
            content= (
                "You are a travel assistant who specializes in answering questions about the best time to travel to destinations, "
            "weather-related timing, peak seasons, off-seasons, and timing advice."
            )),
        HumanMessage(content=state['user_input'])
    ])
        

    return {
        "messages": [response],
        "llm_final_answer": response.content if response.content else "",
    }

# Let's define Place information expert LLM
async def llm_Place(state:State):
    response = await gemini_llm_with_tools.ainvoke([
        SystemMessage(
            content= (
                "You are a travel assistant who specializes in answering questions about the best Places to travel to destinations, "
            "weather-related suitability, peak seasons of events, shopping related scenarios."
            )),
        HumanMessage(content=state['user_input'])
    ])
        

    return {
        "messages": [response],
        "llm_final_answer": response.content if response.content else "",
    }

# Lets define Airline information expert LLM
async def llm_Airline(state:State):
    response = await gemini_llm_with_tools.ainvoke([
        SystemMessage(
            content= (
                "You are a travel assistant who specializes in answering questions about the best airlines to travel to destinations, "
            "flights frequency , peak seasons, cost related scenarios."
            )),
        HumanMessage(content=state['user_input'])
    ])
        

    return {
        "messages": [response],
        "llm_final_answer": response.content if response.content else "",
    }

# Conditional edge function to route to the appropriate node

def route_decision(state:State):

    if state["decision"] == "Time":
        return "llm_Time"
    elif state["decision"] == "Place":
        return "llm_Place"
    elif state["decision"] == "Airline":
        return "llm_Airline"

## Let's Build the Workflow Graph Construction
graph_builder = StateGraph(state_schema=State)

# add nodes in the graph
graph_builder.add_node(node = "llm_Time", action = llm_Time)
graph_builder.add_node(node = "llm_Place", action = llm_Place)
graph_builder.add_node(node= "llm_Airline", action=llm_Airline)
graph_builder.add_node(node= "llm_call_router", action = llm_call_router)

# add edges to connect nodes 
graph_builder.add_edge(START, "llm_call_router")
graph_builder.add_conditional_edges(
       "llm_call_router", 
       route_decision, 
       {"llm_Time":"llm_Time",
        "llm_Place": "llm_Place",
        "llm_Airline":"llm_Airline"},
)

graph_builder.add_edge("llm_Time", END)
graph_builder.add_edge("llm_Place", END)
graph_builder.add_edge("llm_Airline", END)

# Compile workflow 
router_workflow = graph_builder.compile()

# Invoke the workflow asynchronously
async def main():
    state = await router_workflow.ainvoke({"user_input": "What is the best time to visit New York"})
    print(state["llm_final_answer"])

# Run the async main function
import asyncio
asyncio.run(main())
