import asyncio
from src.agents.keywords_agent.graph import run_keyword_agent_stream
from src.sample_user_input import sample_input, sample_input2, sample_input3, sample_input4, sample_input5

async def test_keyword_agent_workflow():
    # await run_keyword_agent_stream(user_input=sample_input2)
    await run_keyword_agent_stream(user_input=sample_input5)

asyncio.run(test_keyword_agent_workflow())