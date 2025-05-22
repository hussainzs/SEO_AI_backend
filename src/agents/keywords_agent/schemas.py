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

class SearchQueries(BaseModel):
    """
    Represent the generated search queries based on the extracted entities and user input.
    """
    search_queries: list[str] = Field(
        ...,
        description= "List of 2 generated search queries based on the extracted entities and user input.",
    )

class keywordMaster_primary_secondarylist(BaseModel):
    """
    Represents the generated keyword masterlist and primary/secondary keywords"""

    masterlist_keywords: list[str] = Field(
        ...,
        description= "List of keywords in the masterlist."
    )

    primary_keywords: list[str] = Field(
        ...,
        description = "List of primary keywords."
    )

    secondary_keywords: list[str] = Field(
        ...,
        description= "list of secondary keywords."
    )


