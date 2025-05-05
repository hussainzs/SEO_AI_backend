from src.agents.test_graph import run_workflow_stream
import asyncio

if __name__ == "__main__":
    # Get user input from the terminal
    user_query: str = input("Enter your question: ")

    # Run the async workflow stream
    asyncio.run(run_workflow_stream(user_input=user_query))
