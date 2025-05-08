import json
from typing import AsyncGenerator
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from src.agents.test_graph import run_workflow_stream
from pydantic import BaseModel

router = APIRouter(prefix=f"/api/test-agent", tags=["AGENT"])

# we subclass BaseModel for automatic input validation using pydantic
class AgentChatRequest (BaseModel):
    """
    Request model for chat requests sent by clients.
    
    Attributes:
        query (str): The user's input query string to be processed by the agent.
    """
    query: str
    

@router.post("/chat/stream", response_model=None)
async def stream_chat(
    agent_chat_request: AgentChatRequest,
) -> StreamingResponse:
    """
    Streams LLM updates and tool calls to the client via SSE.
    """

    async def event_generator() -> AsyncGenerator[str, None]:
        """
        Generates SSE-formatted event strings from the agent workflow stream.
        
        Yields:
            str: Properly formatted SSE data frames containing serialized events
        """
        # Call the agent workflow stream with the user's input query
        async for event in run_workflow_stream(user_input=agent_chat_request.query):
            try:
            # Each `event` is expected to be a dict; serialize it to a JSON string
                payload: str = json.dumps(obj=event)
                # Yield the payload formatted as an SSE 'data:' frame. The double newline ("\n\n") is crucial for SSE message termination
                yield f"data: {payload}\n\n" 
            except TypeError as e:
                # Handle cases where an event might not be JSON serializable
                print(f"Error serializing event to JSON: {e}") 
                error_payload: str = json.dumps(obj={"type": "error", "content": str(e)})
                yield f"data: {error_payload}\n\n"

    headers = {
        "Cache-Control": "no-cache",          # don't cache
        "Connection": "keep-alive",           # keep the HTTP connection open
        "X-Accel-Buffering": "no",            # disable buffering in proxies (e.g. Nginx)
    }

    return StreamingResponse(
        content=event_generator(),
        media_type="text/event-stream",        
        headers=headers,
    )

