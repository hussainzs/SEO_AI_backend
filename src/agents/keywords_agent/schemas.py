"""
For structured outputs we need to define the schema of the output. Define them here for keyword agent.
"""
from typing import Literal
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

class RouteToQueryOrAnalysis(BaseModel):
    """
    Represents the routing decision based on the tool response.
    """
    route: Literal["query_generator", "competitor_analysis"] = Field(
        ...,
        description="Routing decision: either 'query_generator' or 'competitor_analysis'.",
    )
