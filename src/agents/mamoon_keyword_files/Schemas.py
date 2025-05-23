



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


class suggestiongenerator(BaseModel):
    """
    Represent the generated suggestions related to url slug, article titles, and revised sentences with keywords inserted in it
    
    """
    suggested_url_slug: str = Field(
        ...,
        description = "Keyword-rich url slug"
    )

    suggested_article_headlines: list[str] = Field(
        ...,
        description = "List of 2 SEO-optimized keyword-rich article titles"
    )

    final_answer: str = Field(
        ...,
        description = "Revised sentences with incorporation of primary & secondary keywords"
    )