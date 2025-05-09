"""
A minimal FastAPI server that exposes a single SSE endpoint for frontend testing.
!! This should only be run in a local development environment and not in production !!

It emits a sequence of static events, each formatted as a proper SSE "data:" frame,
with a 2-second delay between each event. The emitted objects match the backend's
real SSE output structure for seamless frontend integration testing.

How to run:
    python -m src.api.test_server

Test endpoint (if server running on localhost):
    POST http://127.0.0.1:8000/api/test-agent/chat/stream
"""

import asyncio
import json
from typing import AsyncGenerator
from fastapi import FastAPI, APIRouter
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# ---------------------------------------------------
# Section 1: Define the static SSE events to emit
# ---------------------------------------------------

STATIC_EVENTS: list[dict] = [
    {
        "type": "tool_call",
        "tool_name": "web_search_tool",
        "tool_args": {
            "query": "India Pakistan relations news this week",
            "topic": "news"
        }
    },
    {
        "type": "tool_call",
        "tool_name": "web_search_tool",
        "tool_args": {
            "query": "population of India 2024",
            "topic": "general"
        }
    },
    {
        "type": "tool_call",
        "tool_name": "web_search_tool",
        "tool_args": {
            "query": "population of Pakistan 2024",
            "topic": "general"
        }
    },
    {
        "type": "tool_processing",
        "content": "Processing tool call ..."
    },
    {
        "type": "answer",
        "content": (
            "This week, India and Pakistan have been engaged in military actions. India fired missiles into Pakistani-controlled territory, "
            "and Pakistan shot down several drones. The UN Secretary-General has urged both nations to exercise maximum restraint due to escalating tensions. "
            "(Source: [https://www.chicagotribune.com/2025/05/08/india-pakistan-trade-fire/](https://www.chicagotribune.com/2025/05/08/india-pakistan-trade-fire/), "
            "[https://news.un.org/en/story/2025/05/1162901](https://news.un.org/en/story/2025/05/1162901))\n\n"
            "As of 2024, India's population is estimated at over 1.4 billion (Source: [https://statisticstimes.com/demographics/india/indian-states-population.php](https://statisticstimes.com/demographics/india/indian-states-population.php), "
            "[https://www.worldometers.info/world-population/india-population/](https://www.worldometers.info/world-population/india-population/)). "
            "Pakistan’s population in 2024 is estimated at 251 million (Source: [https://danso.info/en/population-of-pakistan/](https://danso.info/en/population-of-pakistan/), "
            "[https://www.worldometers.info/world-population/pakistan-population/](https://www.worldometers.info/world-population/pakistan-population/))."
        )
    },
    {
        "type": "complete",
        "content": "Workflow completed successfully"
    }
]

# ---------------------------------------------------
# Section 2: FastAPI app and router setup
# ---------------------------------------------------

app: FastAPI = FastAPI(
    title="SSE Test Server",
    version="1.0.0",
    description="A minimal server for frontend SSE integration testing."
)

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

router: APIRouter = APIRouter(prefix="/api/test-agent", tags=["AGENT"])

# ---------------------------------------------------
# Section 3: Request Model
# ---------------------------------------------------

class AgentChatRequest(BaseModel):
    """
    Request model for chat requests sent by clients.

    Attributes:
        query (str): The user's input query string to be processed by the agent.
    """
    query: str

# ---------------------------------------------------
# Section 4: SSE streaming endpoint
# ---------------------------------------------------

@router.post("/chat/stream", response_model=None)
async def stream_chat(agent_chat_request: AgentChatRequest) -> StreamingResponse:
    """
    Streams a fixed sequence of static SSE events to the client, with a 2-second delay between each.

    Args:
        agent_chat_request (AgentChatRequest): The request object containing the user's query.

    Returns:
        StreamingResponse: An HTTP response streaming SSE-formatted data frames.
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        """
        Asynchronously yields each static event as a properly formatted SSE data frame,
        with a 2-second delay between each event.

        Yields:
            str: SSE-formatted string (e.g., 'data: {...}\n\n')
        """
        for event in STATIC_EVENTS:
            try:
                payload: str = json.dumps(obj=event)
                # SSE requires each event to be prefixed with 'data:' and terminated by a double newline
                yield f"data: {payload}\n\n"
            except (TypeError, ValueError) as exc:
                # If serialization fails, emit an error event
                error_payload: str = json.dumps(obj={"type": "error", "content": str(exc)})
                yield f"data: {error_payload}\n\n"
            await asyncio.sleep(2)  # Wait 2 seconds before sending the next event

    headers: dict[str, str] = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }

    return StreamingResponse(
        content=event_generator(),
        media_type="text/event-stream",
        headers=headers,
    )

# ---------------------------------------------------
# Section 5: Register router and run app
# ---------------------------------------------------

app.include_router(router)

if __name__ == "__main__":
    # Run the FastAPI application using uvicorn when this script is executed directly.
    # The server will be available at http://127.0.0.1:8000
    # The SSE test endpoint is: POST http://127.0.0.1:8000/api/test-agent/chat/stream
    uvicorn.run(
        app="src.api.test_server:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )