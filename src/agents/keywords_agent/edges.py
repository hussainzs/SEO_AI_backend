from typing import Literal
from src.agents.keywords_agent.state import KeywordState

# define the conditional edge for routing competitive_analyst node to tools and google_keyword_planner node
def custom_tools_condition(state: KeywordState) -> Literal["tools", "google_keyword_planner"]:
    """
    Use in the conditional_edge to route to the ToolNode if the last message
    has tool calls. Otherwise, route to the google_keyword_planner.
    
    Code inspired by: https://langchain-ai.github.io/langgraph/tutorials/get-started/2-add-tools/#6-define-the-conditional_edges
    
    Args:
        state (KeywordState): The current state of the graph which must contain 'messages' key.
    
    Returns:
        Literal["tools", "google_keyword_planner"]: The next node to route to based on the last message's tool calls.
        
    Raises:
        ValueError: If the 'messages' key is not found in the state or if it is empty.
    """
    # get the messages state
    messages = state.get("messages", [])
    
    # if messages state is empty raise error (this shouldn't happen) otherwise retrieve the last message (which should be AIMessage)
    if messages:
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    
    # check if there are tool calls and there is more than 0 tool calls
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0: # type: ignore
        return "tools"
    else:
        return "google_keyword_planner"