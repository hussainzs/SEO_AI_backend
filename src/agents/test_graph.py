"""
Here we will create a simple langGraph workflow with one tool and get streaming output which will be sent to FastAPI.
We need to use async.
"""

print("\n=== Initializing LangGraph Workflow ===\n")

import os
import json
from json import dumps as json_dump
from pprint import pprint
from typing import Literal, Optional
from dotenv import load_dotenv
from langgraph.graph import StateGraph, MessagesState, START, END

# For defining custom Tools
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from langchain_core.tools.base import ArgsSchema
from pydantic import BaseModel, Field

# Tavily Client
from tavily import (
    TavilyClient,
    AsyncTavilyClient,
)  # provides us the TavilyClient class to interact with the Tavily API

# LLMs
from langchain_google_genai import ChatGoogleGenerativeAI

# For Prompts
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate

# For date time
from datetime import datetime

# *******************Pre Load*******************

print("\n=== Loading Environment Variables and Initializing Clients ===\n")

# Load the environment variables from the .env file
load_dotenv()

# Define the Tavily client for the web search tool.
tavily_api_key: str | None = os.getenv("TAVILY_API_KEY")
if not tavily_api_key:
    raise ValueError(
        "TAVILY_API_KEY environment variable not set."
    )  # In real application, we would do this validation in a separate file.
else:
    print("✓ Tavily API key loaded successfully")

tavily_client = TavilyClient(api_key=tavily_api_key)
async_tavily_client = AsyncTavilyClient(api_key=tavily_api_key)

# Defne Gemini LLM client
gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set.")
else:
    print("✓ Gemini API key loaded successfully")

gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.3,
    max_tokens=2000,
    google_api_key=gemini_api_key,
    max_retries=2,
)


# *** Define the STATE of the graph
print("\n=== Defining State and Tool Classes ===\n")

class State(MessagesState):
    """
    Remember: Subclassing MessageState by LangGraph provides us with a `messages` state automatically with the right reducer.
    """
    llm_final_answer: str


# *** Now lets define the TOOLS we will use in the graph. We define our tool by subclassing BaseTool
# 1. First define the input schema for the tool. This is a simple pydantic model that defines the input parameters for the tool.
class WebSearchToolSchema(BaseModel):
    query: str = Field(
        ...,
        description="The query to search the web for. Formulate this optimized for finding information on the web related to what user needs.",
    )
    topic: Literal["news", "general"] = Field(
        default="general",
        description="The topic to search for. Can be either 'news' or 'general'.",
    )


# 2. Now we define the tool itself. We subclass BaseTool and define the name, description and args_schema.
# We then define the _run method which will be called when the tool is executed. The _run method takes the input parameters and calls the Tavily API to get the search results.
# Note: It's important that every field has type hints. BaseTool is a Pydantic class and not having type hints can lead to unexpected behavior.
class WebSearch(BaseTool):
    name: str = "web_search_tool"
    description: str = (
        """
        Use this tool to search the internet for latest information or any specific information about a topic. 
        If you are asked about news always use this tool with topic 'news'. Your query should be concise (strictly less than 300 characters). 
        The output will include an LLM generated answer. Evaluate the answer and if it is not correct, use the web search results to generate a new answer.
        The output also includes a relevancy score for each source. Higher score means generally more relevant."""
    )
    args_schema: Optional[ArgsSchema] = WebSearchToolSchema

    def _run(
        self,
        query: str,
        topic: Literal["news", "general"] = "general",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        print(f"\n→ Executing web search for query: {query}")
        # Now using LLM generated parameters and some hardcoded ones we will call the Tavily API
        response = tavily_client.search(
            query=query, topic=topic, max_results=2, include_answer=True
        )
        print("✓ Web search completed successfully")
        return json_dump(
            response
        )  # convert the response to a json string as the LLMs expect a string from the tool.

    async def _arun(
        self,
        query: str,
        topic: Literal["news", "general"] = "general",
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        try:
            print(f"\n→ Executing async web search for query: {query}")
            # Perform the asynchronous search with the same parameters as the sync version
            response = await async_tavily_client.search(
                query=query, topic=topic, max_results=2, include_answer=True
            )
            print("✓ Async web search completed successfully")
            return json_dump(response)  # Convert the response to a JSON string
        except Exception as e:
            # Proper error handling with meaningful message
            error_message = f"Asynchronous web search failed: {str(e)}"
            print(f"✗ Error: {error_message}")
            if run_manager:
                await run_manager.on_tool_error(error=e)
            raise RuntimeError(error_message)


# *** 3. Define our prompt
prompt_content = """ 
System Instructions: You are a helpful assistant that can answer questions and provide information based on the latest news and general knowledge.
Use the web search tool for up to date information or news. If you need current time to formulate web query, the current time is {current_time}.

You must provide sources in your answer if you use the web search tool. Use the urls from the web search results to provide sources.
Use the relevancy score and if all scores are low then tell the user you can not answer with high confidence.
If you are not sure about the answer, ask the user for more information or clarify the question.

If user asked a multi part question that needs to be web searched, you can conduct parallel tool calls to the same tool with different queries.
If the queries are related, you can combine the results to provide a comprehensive answer.

Now answer the user question: 
Human: {user_input}
"""

template = ChatPromptTemplate.from_template(prompt_content)

# *** 4. Define the Nodes
# Define tools once at the module level
tools: list[BaseTool] = [WebSearch()]

# Bind tools to LLM once at the module level for efficiency
gemini_llm.bind_tools(tools=tools)

# LLM Node
async def assistant(state: State):
    """
    This node defines the LLM that will interact with user, create tool calls, process tool results and provide final answer.
    """
    print("\n→ Assistant processing current state")
    # call the LLM with the messages we have
    response: BaseMessage = await gemini_llm.ainvoke(state['messages'])
    print("✓ Assistant generated response")
    # update the state
    return {"messages": [response], "llm_final_answer": response.content if response.content else ""}

# Define the conditional edge logic that will decide if LLM made a tool call so route to toolNode or end the graph.
def should_continue(state: State) -> Literal['end'] | Literal['continue']:
    messages = state["messages"]
    most_recent_message: AIMessage = messages[-1] # type: ignore
    # If the last message is not a tool call, then we finish
    if not most_recent_message.tool_calls:
        return "end"
    # default to continue
    return "continue"

# ***5. Define the workflow of the graph
print("\n=== Building Graph Workflow ===\n")

graph_builder = StateGraph(state_schema=State)

# add nodes in the graph
graph_builder.add_node(node="assistant", action=assistant)
graph_builder.set_entry_point("assistant")
graph_builder.add_node(node="tools", action=ToolNode(tools))

# add edges in the graph
graph_builder.add_edge(start_key=START, end_key="assistant")
graph_builder.add_conditional_edges(
    source="assistant", 
    path=should_continue, 
    path_map={
        "continue": "tools",
        "end": END
    }
)
graph_builder.add_edge(start_key="tools", end_key="assistant")

# ****6. Compile the graph - now we can astream this with the inputs needed and it will output.
workflow: CompiledStateGraph = graph_builder.compile()

print("✓ Graph workflow compiled successfully\n")

# *******************End of Graph*******************

async def run_workflow_stream(user_input: str) -> None:
    """
    Runs the LangGraph workflow with streaming output and prints each update to the terminal.

    Args:
        user_input (str): The user's question or request to be processed by the assistant.

    Returns:
        None
    """
    print("\n=== Starting Workflow Execution ===\n")
    print(f"→ Processing user input: {user_input}")
    # Generate current time string
    current_time: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")

    # Format the prompt with user input and current time
    formatted_messages: list[BaseMessage] = template.format_messages(
        user_input=user_input,
        current_time=current_time
    )

    # Prepare the initial state for the workflow
    inputs: dict = {
        "messages": formatted_messages,
        "llm_final_answer": ""
    }
    
    print(f"→ state prepared:")
    pprint(inputs) # Pretty print the initial state for verification
    print("=============================")

    print("\n→ Streaming workflow updates:")
    # Stream the workflow execution and print each update
    try:
        async for update in workflow.astream(input=inputs, stream_mode="updates"):
            print("\n=== Workflow Update ===")
            print(json.dumps(update, indent=4, default=str))
        print("\n✓ Workflow completed successfully")
    except Exception as exc:
        print(f"\n✗ Workflow Error: {exc}")
