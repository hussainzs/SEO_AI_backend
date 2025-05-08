"""
Here we will create a simple langGraph workflow with one tool and get streaming output which will be sent to FastAPI.
"""

# ---------------------------------------------------
# Section 1: Imports and Environment Setup
# ---------------------------------------------------
import os
import json
from typing import Literal, Optional
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
            # Proper error handling with meaningful message
            error_message = f"Asynchronous web search failed: {str(e)}"
            print(f"✗ Error: {error_message}")
            if run_manager:
                await run_manager.on_tool_error(error=e)
            raise RuntimeError(error_message)


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
async def run_workflow_stream(user_input: str) -> None:
    """
    Runs the LangGraph workflow with streaming output and prints each update to the terminal.

    Args:
        user_input (str): The user's question or request to be processed by the assistant.

    Returns:
        None
    """
    # Generate current time string
    current_time: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")

    # Format the prompt with user input and current time
    formatted_messages: list[BaseMessage] = template.format_messages(
        user_input=user_input, current_time=current_time
    )

    # Prepare the initial state for the workflow
    inputs: dict = {"messages": formatted_messages, "llm_final_answer": ""}

    print("\n→ Streaming workflow updates:")
    # Stream the workflow execution and print each update
    try:
        async for update in workflow.astream(
            input=inputs, stream_mode="updates", config={"callbacks": [tracer]}
        ):
            print("\n=== Workflow Update ===")
            # print(json.dumps(update, indent=4, default=str), flush=True)  # save this for debugging if needed.

            # Check if the update dictionary has the 'assistant' key. Otherwise it will have 'tools' key.
            if "assistant" in update:
                # get the object associated with the key 'assistant'
                assistant_output = update.get("assistant", {})

                # Ensure the assistant_output is not empty and has the 'messages' key
                if not assistant_output or not assistant_output.get("messages"):
                    continue

                # Get the stuff inside 'messages' array. We get the first index because "updates" mode only adds one message at a time in the array.
                assistant_message = assistant_output["messages"][0]

                # CASE 1: Check for TOOL CALLS and make sure they are not empty
                if hasattr(assistant_message, "tool_calls") and assistant_message.tool_calls:
                    # Some models like GPT 4.1 can output content and tool calls in the same message. This if condition is for them.
                    if assistant_message.content:
                        print(f"LLM Answer: {assistant_message.content}", flush=True)
                        
                    # loop through tool calls because there may be multiple tool calls. tool_calls is a list of dicts.
                    for tool_call in assistant_message.tool_calls:
                        tool_name = tool_call.get("name", "unknown_tool")
                        tool_args = tool_call.get("args", {})

                        # Format the arguments nicely: key1="value1", key2="value2"
                        args_str = ", ".join(f'{k}="{v}"' for k, v in tool_args.items())
                        print(f"Tool Call to {tool_name}: Ran with arguments: {args_str}", flush=True)

                # CASE 2: Check for FINAL ANSWER (content without tool calls)
                # Check if content is present and non empty AND ensure tool_calls is empty or not present
                elif hasattr(assistant_message, "content") and assistant_message.content and not (
                        hasattr(assistant_message, "tool_calls") and assistant_message.tool_calls
                    ):
                    print(f"LLM Answer: {assistant_message.content}", flush=True)
                # ---------------------------------------------------
                
            # for tool processing, we will only show tool processing, tool results can be large and we will not yield them.
            elif "tools" in update:
                print("Processing tool call ...", flush=True)
            else:
                # this shouldn't happen but just in case some shit happens
                print(
                    "\n-------------- GOT UNKNOWN TYPE OF NODE -------- CHECK output!",
                    flush=True,
                )
                print(f"Unknown node type: {update}", flush=True)

        # try block finished so output workflow done. 
        print("\n====✓✓ Workflow completed successfully")

    except Exception as exc:
        print(f"\n✗ Workflow Error: {exc}")
