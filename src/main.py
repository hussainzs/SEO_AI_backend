"""
This is the main FastAPI entrypoint to be run for starting the server

Run python -m src.main
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.keyword_agent_route import router as keyword_agent_router
from src.api.full_article_suggestions_route import router as full_article_suggestions_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Test Agent API",
        version="1.0.0",
    )

    # allow all origins — will adjust in production!
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )    # mount routes here
    app.include_router(keyword_agent_router)
    app.include_router(full_article_suggestions_router)
    return app

# initialize the FastAPI app
app: FastAPI = create_app()

if __name__ == "__main__":
    # Run the FastAPI application on localhost for development
    uvicorn.run(
        app="src.main:app",  # Specify the app location
        host="127.0.0.1",  # Bind to localhost
        port=8000,  # Use port 8000
        reload=True,  # Enable auto-reload for development
    )
