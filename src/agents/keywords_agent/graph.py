# Langgraph imports
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.state import CompiledStateGraph

# our custom state, tools, nodes
from src.agents.keywords_agent.state import KeywordState
from src.tools.web_search_tool import WebSearch
from src.agents.keywords_agent.nodes import (
    entity_extractor,
    competitor_analyst,
    google_keyword_planner,
    masterlist_and_primary_keyword_generator,
    suggestions_generator,
)
from src.utils.settings import settings, get_key

# For Opik observability
from opik.integrations.langchain import OpikTracer

opik_api_key: str | None = get_key(settings.OPIK_API_KEY)
opik_workspace: str | None = get_key(settings.OPIK_WORKSPACE)
opik_project_name: str | None = get_key(settings.OPIK_PROJECT_NAME)

# initialize graph
graph_builder = StateGraph(state_schema=KeywordState)

# initialize tools
tool_list = [WebSearch()]

# Add Nodes
graph_builder.add_node(node="entity_extractor", action=entity_extractor)
graph_builder.add_node(node="competitor_analyst", action=competitor_analyst)
graph_builder.add_node(node="tools", action=ToolNode(tools=tool_list))
graph_builder.add_node(node="google_keyword_planner", action=google_keyword_planner)
graph_builder.add_node(
    node="masterlist_and_primary_keyword_generator",
    action=masterlist_and_primary_keyword_generator,
)
graph_builder.add_node(node="suggestions_generator", action=suggestions_generator)

# Add Edges
graph_builder.add_edge(start_key=START, end_key="entity_extractor")
graph_builder.add_edge(start_key="entity_extractor", end_key="competitive_analyst")

# if this confuses you refer to: https://www.baihezi.com/mirrors/langgraph/reference/prebuilt/index.html#tools_condition
graph_builder.add_conditional_edges(
    source="competitive_analyst",
    path=tools_condition,
    path_map={
        # If it returns 'action', route to the 'tools' node
        "action": "tools",
        # If it returns '__end__', route to the 'google_keyword_planner' node
        "__end__": "google_keyword_planner",
    },
)

# this is a loopback edge to allow the agent to retry the tool call
graph_builder.add_edge(
    start_key="tools",
    end_key="competitive_analyst",
)
graph_builder.add_edge(
    start_key="google_keyword_planner",
    end_key="masterlist_and_primary_keyword_generator",
)
graph_builder.add_edge(
    start_key="masterlist_and_primary_keyword_generator",
    end_key="suggestions_generator",
)
graph_builder.add_edge(
    start_key="suggestions_generator",
    end_key=END,
)

# Compile the graph
keyword_agent: CompiledStateGraph = graph_builder.compile()

# Add Opik Tracer
tracer = OpikTracer(
    graph=keyword_agent.get_graph(xray=True), project_name=opik_project_name
)


# Run the agent
async def run_keyword_agent_stream(user_input: str):

    async for update in keyword_agent.astream(
        input={"messages": user_input},
        stream_mode="updates",
        config={"callbacks": [tracer]},
    ):
        print(update)
