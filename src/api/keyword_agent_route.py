import json
from typing import AsyncGenerator
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.agents.keywords_agent.graph import run_keyword_agent_stream

router = APIRouter(prefix=f"/agent/keyword", tags=["KEYWORD_AGENT"])

class KeywordAgentRequest (BaseModel):
    """
    Request model for chat requests sent by clients.
    
    Attributes:
        query (str): The user's input query string to be processed by the agent.
    """
    user_article: str
    
@router.post("/stream", response_model=None)
async def stream_keyword_agent(request: KeywordAgentRequest) -> StreamingResponse:
    
    async def event_generator() -> AsyncGenerator[str, None]:
        """
        Generates SSE-formatted event strings from the agent workflow stream.
        
        Yields:
            str: Properly formatted SSE data frames containing serialized events
        """
        # Call the agent workflow stream with the user's input query
        async for event in run_keyword_agent_stream(user_input=request.user_article):
            # Each `event` is expected to be a dict; serialize it to a JSON string
            payload: str = json.dumps(obj=event)
            
            # Yield the payload formatted as an SSE 'data:' frame. The double newline ("\n\n") is crucial for SSE message termination
            yield f"data: {payload}\n\n" 

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

