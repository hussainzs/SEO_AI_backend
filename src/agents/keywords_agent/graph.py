# Langgraph imports
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.state import CompiledStateGraph

# our custom state, tools, nodes
from src.agents.keywords_agent.state import KeywordState
from src.tools.web_search_tool import WebSearch, dummy_web_search_tool
from src.agents.keywords_agent.edges import route_to_query_or_analysis
from src.agents.keywords_agent.nodes import (
    entity_extractor,
    query_generator,
    competitor_analysis,
    google_keyword_planner1,
    google_keyword_planner2,
    keyword_data_synthesizer,
    masterlist_and_primary_keyword_generator,
    suggestions_generator,
    router_and_state_updater,
)
from src.utils.settings import settings, get_key

# For Opik observability
from opik.integrations.langchain import OpikTracer

opik_api_key: str | None = get_key(settings.OPIK_API_KEY)
opik_workspace: str | None = get_key(settings.OPIK_WORKSPACE)
opik_project_name: str | None = get_key(settings.OPIK_PROJECT_NAME)

# LangSmith observability (langChain automatically detects the environment variables)
import dotenv

dotenv.load_dotenv()

# initialize graph
graph_builder = StateGraph(state_schema=KeywordState)

# initialize tools
tool_list = [WebSearch()]
# tool_list = [dummy_web_search_tool]  # testing

# Add Nodes
graph_builder.add_node(node="entity_extractor", action=entity_extractor)
graph_builder.add_node(node="query_generator", action=query_generator)
graph_builder.add_node(node="competitor_analysis", action=competitor_analysis)
graph_builder.add_node(node="web_search_tool", action=ToolNode(tools=tool_list))
graph_builder.add_node(node="router_and_state_updater", action=router_and_state_updater)
graph_builder.add_node(node="google_keyword_planner1", action=google_keyword_planner1)
graph_builder.add_node(node="google_keyword_planner2", action=google_keyword_planner2)
graph_builder.add_node(node="keyword_data_synthesizer", action=keyword_data_synthesizer)
graph_builder.add_node(
    node="masterlist_and_primary_keyword_generator",
    action=masterlist_and_primary_keyword_generator,
)
graph_builder.add_node(node="suggestions_generator", action=suggestions_generator)

# Add Edges
graph_builder.add_edge(start_key=START, end_key="entity_extractor")
graph_builder.add_edge(start_key="entity_extractor", end_key="query_generator")

# if this confuses you refer to: https://www.baihezi.com/mirrors/langgraph/reference/prebuilt/index.html#tools_condition
graph_builder.add_conditional_edges(
    source="query_generator",
    path=tools_condition,
    path_map={
        # If it returns 'action', route to the 'web_search_tool' node
        "tools": "web_search_tool",
        # If it returns '__end__', route to the 'router_and_state_updater' node. This should never happen but just in case.
        "__end__": "router_and_state_updater",
    },
)
graph_builder.add_edge(start_key="web_search_tool", end_key="router_and_state_updater")

# this is a loopback edge to allow the agent to retry the tool call
graph_builder.add_conditional_edges(
    source="router_and_state_updater",
    path=route_to_query_or_analysis,
    path_map={
        "query_generator": "query_generator",
        "competitor_analysis": "competitor_analysis",
    },
)
# add parallel edges from competitor_analysis to google_keyword_planner1 and google_keyword_planner2
graph_builder.add_edge(
    start_key="competitor_analysis",
    end_key="google_keyword_planner1",
)
graph_builder.add_edge(
    start_key="competitor_analysis",
    end_key="google_keyword_planner2",
)
# add edges from google_keyword_planner1 and google_keyword_planner2 to keyword_data_synthesizer
graph_builder.add_edge(
    start_key="google_keyword_planner1",
    end_key="keyword_data_synthesizer",
)
graph_builder.add_edge(
    start_key="google_keyword_planner2",
    end_key="keyword_data_synthesizer",
)
# now synthesizer will route to masterlist_and_primary_keyword_generator
graph_builder.add_edge(
    start_key="keyword_data_synthesizer",
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
        input={"messages": user_input, "user_input": user_input},
        stream_mode="custom",
        config={"callbacks": [tracer]},
    ):
        print("\n\n******************")
        print(update)
        print("\n")
