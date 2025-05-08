# entrypoint: create FastAPI app and import routes

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.test_route import router as test_agent_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="Test Agent API",
        version="1.0.0",
    )

    # allow all origins—adjust in prod!
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # mount your streaming chat endpoint
    app.include_router(test_agent_router)
    return app

app: FastAPI = create_app()

if __name__ == "__main__":
    # Run the FastAPI application on localhost
    uvicorn.run(
        app="src.main:app",  # Specify the app location
        host="127.0.0.1",    # Bind to localhost
        port=8000,           # Use port 8000
        reload=True,         # Enable auto-reload for development
    )



