"""
For structured outputs we need to define the schema of the output. Define them here for keyword agent.
"""
from html import entities
from pydantic import BaseModel, Field

class Entities(BaseModel):
    """
    Represents the extracted entities from the user input.
    """
    entities: list[str] = Field(
        ...,
        description="List of 3 extracted entities from the user input.",
    )
