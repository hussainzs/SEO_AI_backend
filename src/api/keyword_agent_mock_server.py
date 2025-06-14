"""
Minimal mock server for testing the keyword agent API with frontend.
It will emit a sequence of static events formatted as SSE "data:" frames just like the real agent API and accepts the same request format.
It does not consume any real agent logic or data, thus saving us LLM calls and API costs.

Run this server with: python -m src.api.keyword_agent_mock_server
"""

# import static data and request model
from src.api.keyword_agent_route import KeywordAgentRequest, router
from src.api.mock_server_data import STATIC_DATA, MOCK_FULL_ARTICLE_SUGGESTION
from src.api.full_article_suggestions_route import FullArticleSuggestionResponse

import asyncio
import json
from typing import AsyncGenerator
from fastapi import FastAPI, APIRouter
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app: FastAPI = FastAPI(
    title="SSE Mock Server for Keyword Agent",
    version="0.1.0",
    description="A minimal server for frontend SSE integration testing.",
)

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

router: APIRouter = APIRouter(prefix="/api/test/keyword", tags=["AGENT"])

@router.post("/stream", response_model=None)
async def stream_mock_keyword_agent(request: KeywordAgentRequest) -> StreamingResponse:
    async def event_generator() -> AsyncGenerator[str, None]:
        counter: int = 0
        for event in STATIC_DATA:
            payload: str = json.dumps(obj=event)
            counter += 1
            # mimic the realistc delay for different types of events, I'm just gonna manually set the delay for each event as I already know and this is for testing
            match counter:
                case 2:
                    # await asyncio.sleep(3.7)
                    await asyncio.sleep(5)
                case 5:
                    await asyncio.sleep(2)
                case 8:
                    await asyncio.sleep(2.2)
                case 10:
                    # await asyncio.sleep(37)
                    await asyncio.sleep(3)
                case 13:
                    # await asyncio.sleep(6)
                    await asyncio.sleep(2)
                case 15:
                    await asyncio.sleep(1)
                case 17:
                    # await asyncio.sleep(20)
                    await asyncio.sleep(3)
                case 20:
                    # await asyncio.sleep(13)
                    await asyncio.sleep(2.5)

            yield f"data: {payload}\n\n"

    headers: dict[str, str] = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }

    return StreamingResponse(event_generator(), media_type="text/event-stream", headers=headers)


@router.post("/suggestfullarticle", response_model=FullArticleSuggestionResponse)
async def mock_generate_full_article_suggestion() -> FullArticleSuggestionResponse:
    """
    Mock endpoint for generating full article suggestions.

    This endpoint returns static mock data for testing the frontend integration
    without making actual LLM calls or consuming API resources.

    Returns:
        FullArticleSuggestionResponse: Mock response containing a sample article suggestion
    """  # Add a small delay to simulate processing time
    await asyncio.sleep(delay=1.5)

    # Return the mock full article suggestion data with proper type handling
    return FullArticleSuggestionResponse(
        success=bool(MOCK_FULL_ARTICLE_SUGGESTION["success"]),
        article_suggestion=str(MOCK_FULL_ARTICLE_SUGGESTION["article_suggestion"]),
        message=str(MOCK_FULL_ARTICLE_SUGGESTION["message"]),
    )


app.include_router(router)

if __name__ == "__main__":
    # Run the FastAPI application using uvicorn when this script is executed directly.
    # The server will be available at http://127.0.0.1:8000
    # Available endpoints:
    # - SSE test endpoint: POST http://127.0.0.1:8000/api/test/keyword/stream
    # - Full article suggestion: POST http://127.0.0.1:8000/api/test/keyword/suggestfullarticle
    uvicorn.run(
        app="src.api.keyword_agent_mock_server:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
