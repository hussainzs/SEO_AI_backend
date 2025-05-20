
from src.agents.keywords_agent.state import KeywordState
from src.tools.web_search_tool import WebSearch
from src.utils.models_initializer import get_gemini_model
from langgraph.graph import MessagesState

# Let's import all the tools in the single list so, that LLM call it any tool from it.
def tools_list() -> list:
    "returns the list of tools"
    return [
            WebSearch()]

# Initialize the tools 
def tools(KeywordState: MessagesState):
    return tools_list.invoke(KeywordState)

