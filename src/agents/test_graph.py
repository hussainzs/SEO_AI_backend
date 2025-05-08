"""
Here we will create a simple langGraph workflow with one tool and get streaming output which will be sent to FastAPI.
"""

# ---------------------------------------------------
# Section 1: Imports and Environment Setup
# ---------------------------------------------------
import os
import json
from typing import AsyncGenerator, AsyncIterator, Literal, Optional
from dotenv import load_dotenv

# For Graph State
from langgraph.graph import StateGraph, MessagesState, START

# For defining custom Tools
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition
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
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate

# For date time
from datetime import datetime

# For Opik observability
from opik.integrations.langchain import OpikTracer

# *******************Pre Load*******************

# Load the environment variables from the .env file
load_dotenv()

# ---------------------------------------------------
# Section 2: Opik API Key and Workspace Validation
# ---------------------------------------------------
# Define the LangFuse callback handler for observability
opik_api_key: str | None = os.getenv("OPIK_API_KEY")
opik_workspace: str | None = os.getenv("OPIK_WORKSPACE")
opik_project_name: str | None = os.getenv("OPIK_PROJECT_NAME")
if not opik_api_key or not opik_workspace:
    raise ValueError(
        "OPIK_API_KEY and OPIK_WORKSPACE environment variables not set."
    )  # In real application, we would do this validation in a separate file.


# ---------------------------------------------------
# Section 3: Tavily Client Initialization
# ---------------------------------------------------
# Define the Tavily client for the web search tool.
tavily_api_key: str | None = os.getenv("TAVILY_API_KEY")
if not tavily_api_key:
    raise ValueError(
        "TAVILY_API_KEY environment variable not set."
    )  # In real application, we would do this validation in a separate file.

tavily_client = TavilyClient(api_key=tavily_api_key)
async_tavily_client = AsyncTavilyClient(api_key=tavily_api_key)


# ---------------------------------------------------
# Section 4: Gemini LLM Client Initialization
# ---------------------------------------------------
def return_gemini_agent() -> ChatGoogleGenerativeAI:
    """Returns the Gemini LLM client instance."""

    # Defne Gemini LLM client
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")

    gemini_llm = ChatGoogleGenerativeAI(
        # model="gemini-2.5-flash-preview-04-17",
        # model="gemini-1.5-pro",
        # model="gemini-2.5-pro-exp-03-25",
        model="gemini-2.0-flash",
        temperature=0.3,
        max_tokens=2000,
        google_api_key=gemini_api_key,
        max_retries=2,
    )
    return gemini_llm


# ---------------------------------------------------
# Section 5: State Definition for LangGraph
# ---------------------------------------------------
class State(MessagesState):
    """
    Remember: Subclassing MessageState by LangGraph provides us with a `messages` state automatically with the right reducer.
    """
    llm_final_answer: str

# ---------------------------------------------------
# Section 6: Web Search Tool Definition
# ---------------------------------------------------
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
        "Searches the internet using the Tavily API for up-to-date information or specific details on a 'query'."
        "Specify 'topic' as 'news' for current events, otherwise use 'general'."
        "Provides search results, potentially including a summarized answer and source relevancy scores."
        "Keep the 'query' concise (under 300 characters)."
    )
    args_schema: Optional[ArgsSchema] = WebSearchToolSchema

    def _run(
        self,
        query: str,
        topic: Literal["news", "general"] = "general",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:

        # Now using LLM generated parameters and some hardcoded ones we will call the Tavily API
        response = tavily_client.search(
            query=query, topic=topic, max_results=2, include_answer=True
        )

        return json.dumps(
            response
        )  # convert the response to a json string as the LLMs expect a string from the tool.

    async def _arun(
        self,
        query: str,
        topic: Literal["news", "general"] = "general",
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        try:
            # Perform the asynchronous search with the same parameters as the sync version
            response = await async_tavily_client.search(
                query=query, topic=topic, max_results=2, include_answer=True
            )
            return json.dumps(response)  # Convert the response to a JSON string
        except Exception as e:
            error_message = f"Asynchronous web search failed: {str(e)}"
            print(f"✗ Error: {error_message}") # Keep server-side log for this
            
            if run_manager:
                await run_manager.on_tool_error(error=e, name=self.name) # Pass tool name
                
            # Return a JSON string with the error message for the LLM to reflect on
            return json.dumps({"error": error_message, "tool_name": self.name})


# ---------------------------------------------------
# Section 7: Tool Registration and Tool Binding with LLM
# ---------------------------------------------------
def get_tools() -> list[BaseTool]:
    """
    Returns a list of tools to be used in the graph.
    """
    return [WebSearch()]


def get_model_with_tools():
    """
    Returns the LLM model with tools bound to it.
    """
    # Define the LLM model and bind the tools to it
    gemini_llm: ChatGoogleGenerativeAI = return_gemini_agent()
    gemini_llm_with_tools = gemini_llm.bind_tools(tools=get_tools())
    return gemini_llm_with_tools


# ---------------------------------------------------
# Section 8: Prompt Template Definition
# ---------------------------------------------------
# *** Define our prompt (we avoid a separate system prompt because some models don't support it. Instead we use a single prompt template with the system instructions inside it.)
prompt_content = """ 
System Instructions: You are a helpful assistant that can answer questions and provide information based on the latest news and general knowledge.
Call the web search tool for up to date information on news or latest events. If you need current time to formulate web query, the current time is {current_time}.
When you call the tool, you must provide valid parameters for the tool. If you get no response from the tool, say that to the user and show whatever output came from the tool.
IF YOU ARE ASKED TO MULTIPLY TWO NUMBERS YOU MUST CALL THE MULTIPLY TOOL WITH THE PARAMETERS a and b AND RETURN THE RESULT FROM THE TOOL.
You must provide sources in your answer if you use the web search tool. Use the urls from the web search results to provide sources.

Special Note: If user asks what tools you have access to then return a json format with all the information you have about the tool since user is debugging the system.

Now answer the user question: 
Human: {user_input}
"""

template = ChatPromptTemplate.from_template(prompt_content)

# ---------------------------------------------------
# Section 9: Node Definitions for LangGraph
# ---------------------------------------------------

# get the model with tools so we can use it inside the assistant node below. Don't define it inside the node because it will be called multiple times and slow down the process.
gemini_llm_with_tools = get_model_with_tools()


# LLM Node
async def assistant(state: State):
    """
    This node defines the LLM that will interact with user, create tool calls, process tool results and provide final answer.
    """
    response: BaseMessage = await gemini_llm_with_tools.ainvoke(state['messages'])
    
    # update the state
    return {
        "messages": [response],
        "llm_final_answer": response.content if response.content else "",
    }

# ---------------------------------------------------
# Section 10: Workflow Graph Construction
# ---------------------------------------------------

graph_builder = StateGraph(state_schema=State)

# add nodes in the graph
graph_builder.add_node(node="assistant", action=assistant)
graph_builder.add_node(node="tools", action=ToolNode(tools=get_tools()))

# add edges in the graph
graph_builder.add_edge(start_key=START, end_key="assistant")
graph_builder.add_conditional_edges(
    source="assistant",
    path=tools_condition,
    # prebuilt tools_condition will route to node called "tools" if the LLM made a tool call, otherwise it will route to END.
)
graph_builder.add_edge(start_key="tools", end_key="assistant")

# Compile the graph - now we can astream this with the inputs needed and it will output.
workflow: CompiledStateGraph = graph_builder.compile()

# Create the Opik tracer for observability
tracer = OpikTracer(graph=workflow.get_graph(xray=True), project_name=opik_project_name)

# ---------------------------------------------------
# Section 11: Workflow Execution with Streaming Output
# ---------------------------------------------------
async def run_workflow_stream(user_input: str) -> AsyncGenerator[dict, None]:
    """
    Runs the LangGraph workflow with streaming output and yields updates as a dictionary.

    Args:
        user_input (str): The input string provided by the user to initiate the workflow.
        dict: A JSON-serializable dictionary representing the workflow's state. Possible 
        dictionary structures include:
            - {"type": "answer", "content": str}:
                Represents an answer or response generated by the workflow.
                
            - {"type": "tool_call", "tool_name": str, "tool_args": dict}:
                Indicates a tool call with the tool's name and arguments.
                
            - {"type": "tool_processing", "content": str}:
                Signals that a tool call is being processed.
                
            - {"type": "complete", "content": str}:
                Indicates successful completion of the workflow.
                
            - {"type": "error", "content": str}:
                Contains an error message if an exception occurs during the workflow.
    Raises:
        Exception: Any exception encountered during the execution of the workflow is caught 
        and yielded as an error update.
    """
    
    # Prepare messages and inputs
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    formatted_messages = template.format_messages(
        user_input=user_input, current_time=current_time
    )
    
    inputs = {"messages": formatted_messages, "llm_final_answer": ""}

    try:
        async for update in workflow.astream(
            input=inputs, stream_mode="updates", config={"callbacks": [tracer]}
        ):
            # Check if the update dictionary has the 'assistant' key. Otherwise it will have 'tools' key.
            if "assistant" in update:
                assistant_output = update["assistant"]
                # if there is no messages key then we can't do anything so skip
                if not assistant_output.get("messages"):
                    continue
                
                # messages is a array where each update contains only one element in the array. get this element
                msg = assistant_output["messages"][0]

                # CASE: Check for TOOL CALLS and make sure they are not empty
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    # loop through tool calls because there may be multiple tool calls. tool_calls is a list of dicts.
                    for tool_call in msg.tool_calls:
                        name = tool_call.get("name", "unknown_tool")
                        args = tool_call.get("args", {})
                        yield {
                            "type": "tool_call",
                            "tool_name": name,
                            "tool_args": args or {},
                        }

                # CASE: pure LLM answer (content without tool calls)
                elif msg.content:
                    yield {"type": "answer", "content": msg.content}

            elif "tools" in update:
                yield {"type": "tool_processing", "content": "Processing tool call ..."}

        # print("\n====✓✓ Workflow completed successfully")
        yield {"type": "complete", "content": "Workflow completed successfully"}

    except Exception as exc:
        yield {"type": "error", "content": str(exc)}
