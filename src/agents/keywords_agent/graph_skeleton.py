"""
We will draw the Graph skeleton Image for the given nodes. 
"""

from langgraph.graph import StateGraph, MessageGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from IPython.display import display, Image
from src.agents.keywords_agent.nodes import entity_extractor, competitive_analyst, google_keyword_planner, masterlist_and_primary_keyword_generator, suggestions_generator
from src.agents.keywords_agent.state import KeywordState
from src.tools.web_search_tool import WebSearch
from src.tools.tools_initializer import tools, tools_list
from langgraph.prebuilt import tools_condition, ToolNode
from langchain_core.runnables.graph_png import PngDrawer

# Adding the nodes to the graph
graph_builder = StateGraph(state_schema=KeywordState)

graph_builder.add_node(node = "entity_extractor", action= entity_extractor)
graph_builder.add_node(node="competitive_analyst",action=competitive_analyst)
graph_builder.add_node(node="google_keyword_planner", action=google_keyword_planner)
graph_builder.add_node(node="masterlist_and_primary_keyword_generatir", action=masterlist_and_primary_keyword_generator)
graph_builder.add_node(node="toolnode", action = tools)
graph_builder.add_node(node="tools", action=ToolNode(tools_list()))
graph_builder.add_node(node="suggestions_generator", action=suggestions_generator)

# Adding the edges to the graph

graph_builder.add_edge(start_key=START, end_key="entity_extractor")
graph_builder.add_edge("entity_extractor","competitive_analyst")
graph_builder.add_conditional_edges(
    "competitive_analyst",
    tools_condition,
    {"tools":"tools", "__end__": END}
)

graph_builder.add_edge("tools", "google_keyword_planner")
graph_builder.add_edge("google_keyword_planner", "masterlist_and_primary_keyword_generatir")
graph_builder.add_edge("masterlist_and_primary_keyword_generatir", "suggestions_generator")
graph_builder.add_edge("suggestions_generator", END)

# Compiling the graph

keyword_feature_graph = graph_builder.compile()
