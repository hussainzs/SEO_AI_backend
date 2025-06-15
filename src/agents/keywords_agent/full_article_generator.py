# Generate a full article suggestion when this LLM runs
from langchain_core.messages import HumanMessage

from src.utils.models_initializer import (
    initialize_model_with_fallbacks,
    get_mistral_model,
    get_openai_model,
)

from src.agents.keywords_agent.schemas import FullArticleGeneratorModel

from src.agents.keywords_agent.prompts import FULL_ARTICLE_SUGGESTION_PROMPT

from src.agents.keywords_agent.intermediate_state import (
    get_original_article_draft,
    get_sentence_level_suggestions
)

MODEL_WITH_FALLBACK_AND_STRUCTURED = initialize_model_with_fallbacks(
    primary_model_fn=get_openai_model,
    primary_model_kwargs={"model_num": 1, "temperature": 0.2},
    fallback_model_fns=[get_mistral_model, get_openai_model],
    fallback_model_kwargs_list=[
        {"model_num": 1, "temperature": 0.2},
        {"model_num": 2, "temperature": 0.2},
    ],
    structured_output_schema=FullArticleGeneratorModel,
)


async def suggest_full_article() -> str:
    """
    suggest a full revised article using the sentence level suggestions suggested earlier. We assume suggestions.txt already has the sentence level suggestions.
    for now this is a quick hack, later we will integrate this using subgraphs or add this as a node to the keywords agent graph.

    Returns:
        str: The full article suggestion.
    """
    # format the prompt with the original article draft and sentence level suggestions
    prompt = FULL_ARTICLE_SUGGESTION_PROMPT.format(
        original_article_draft=get_original_article_draft(),
        sentence_level_suggestions=get_sentence_level_suggestions(),
    )

    # Generate the full article suggestion using the model
    full_article_suggestion: FullArticleGeneratorModel = await MODEL_WITH_FALLBACK_AND_STRUCTURED.ainvoke([HumanMessage(content=prompt)])  # type: ignore

    return full_article_suggestion.content