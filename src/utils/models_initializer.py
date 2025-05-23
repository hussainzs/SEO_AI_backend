"""
here we initialize our langchain models and web search sdks so we can just import them in rest of our app.
"""

from typing import Any, Callable, Union
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mistralai import ChatMistralAI
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from tavily import (
    TavilyClient,
    AsyncTavilyClient,
)
from exa_py import Exa, AsyncExa
from pydantic import SecretStr
from src.utils.settings import settings, get_key
from pydantic import BaseModel

# Define a type alias for valid chat models
ChatModel = Union[ChatGoogleGenerativeAI, ChatGroq, ChatOpenAI, ChatMistralAI]


def get_openai_model(model_num: int = 1, temperature: float = 0.5) -> ChatOpenAI:
    """
    Initialize the OpenAI LLM with the specified model name (number to name mapping for ease of future changes)

    Warning: ensure if you use structured output your pydantic model schema matches OpenAI's supported schema: https://platform.openai.com/docs/guides/structured-outputs?api-mode=chat#supported-schemas

    Available model names:

    - (1) "gpt-4.1-mini"
    - (2) "o4-mini-2025-04-16"

    Args:
        model_num (int): The number of the model to use. Defaults to (1) which is "gpt-4.1-mini".
        temperature (float): The temperature for the model. Defaults to 0.5.

    Returns:
        ChatOpenAI: The initialized OpenAI LLM instance of ChatOpenAI from Langchain integration.
    """

    # Get the API key from settings
    openai_api_key: SecretStr | None = settings.OPENAI_API_KEY
    if openai_api_key is None:
        raise ValueError(
            "OpenAI API key is not set in the environment variables. Check your environment variables"
        )

    # Map the model number to the actual model name
    model_mapping = {
        1: "gpt-4.1-mini",
        2: "o4-mini-2025-04-16",
    }

    # o4 mini doesnt support temperature so we wont pass it
    if model_num == 2:
        openai_llm = ChatOpenAI(
            model=model_mapping.get(model_num, "o4-mini-2025-04-16"),
            api_key=openai_api_key,
            max_retries=2,
        )
    else:
        openai_llm = ChatOpenAI(
            model=model_mapping.get(model_num, "gpt-4.1-mini"),
            temperature=temperature,
            api_key=openai_api_key,
            max_retries=2,
        )

    return openai_llm


# Mistral LLM
def get_mistral_model(model_num: int = 1, temperature: float = 0.5) -> ChatMistralAI:
    """
    Initialize the Mistral LLM. Currently we only support one model.
    Available model names:

    - (1) "mistral-medium-2505"

    Args:
        model_num (int): The number of the model to use. Defaults to (1) which is "mistral-medium-2505".
        temperature (float): The temperature for the model. Defaults to 0.5.

    Returns:
        ChatMistralAI: The initialized Mistral LLM instance of ChatMistralAI from Langchain integration.
    """

    # Get the API key from settings
    mistral_api_key: SecretStr | None = settings.MISTRAL_API_KEY
    if mistral_api_key is None:
        raise ValueError(
            "Mistral API key is not set in the environment variables. Check your environment variables"
        )

    # Map the model number to the actual model name
    model_mapping = {
        1: "mistral-medium-2505",
    }

    # Initialize the Mistral LLM with the specified model name
    mistral_llm = ChatMistralAI(
        model_name=model_mapping.get(model_num, "mistral-medium-2505"),
        temperature=temperature,
        api_key=mistral_api_key,
        max_retries=2,
    )

    return mistral_llm


# Gemini LLM
def get_gemini_model(
    model_name: int = 1, temperature: float = 0.5
) -> ChatGoogleGenerativeAI:
    """
    Initialize the Gemini LLM with the specified model name.
    Available model names:

    - (1) "gemini-2.0-flash"
    - (2) "gemini-2.5-flash-preview-04-17"
    - (3) "gemini-2.5-pro-exp-03-25"
    - (4) "gemini-1.5-pro"

    \nFor latest available models: https://ai.google.dev/gemini-api/docs/models#model-variations
    \nFor Langchain integration: https://python.langchain.com/api_reference/google_genai/chat_models/langchain_google_genai.chat_models.ChatGoogleGenerativeAI.html


    Args:
        model_name (int): The number of model to use. Defaults to (1) which is "gemini-2.0-flash".
        temperature (float): The temperature for the model. Defaults to 0.5.

    Returns:
        ChatGoogleGenerativeAI: The initialized Gemini LLM instance of ChatGoogleGenerativeAI from Langchain integration.
    """

    # Get the API key from settings
    gemini_api_key: str | None = get_key(api_key=settings.GEMINI_API_KEY)
    if gemini_api_key is None:
        raise ValueError(
            "Gemini API key is not set in the environment variables. Check your environment variables"
        )

    # Map the model number to the actual model name
    model_mapping = {
        1: "gemini-2.0-flash",
        2: "gemini-2.5-flash-preview-04-17",
        3: "gemini-2.5-pro-exp-03-25",
        4: "gemini-1.5-pro",
    }

    # Initialize the Gemini LLM with the specified model name
    gemini_llm = ChatGoogleGenerativeAI(
        model=model_mapping.get(model_name, "gemini-2.0-flash"),
        temperature=temperature,
        google_api_key=gemini_api_key,
        max_retries=2,
    )

    return gemini_llm


# Groq LLM
def get_groq_model(model_name: int = 1, temperature: float = 0.2) -> ChatGroq:
    """
    Initialize the Groq LLM with the specified model name.
    Available model names (numbers mapping to models):

    For LangChain Integration:https://python.langchain.com/api_reference/groq/chat_models/langchain_groq.chat_models.ChatGroq.html
    \nFor the latest available models: https://console.groq.com/docs/models
    \nFor rate limits: https://console.groq.com/dashboard/limits

    - (1) "llama3-70b-8192"
    - (2) "deepseek-r1-distill-llama-70b"
    - (3) "meta-llama/llama-4-scout-17b-16e-instruct"

    Args:
        model_name (int): The number of the model to use. Defaults to (1) which is "llama3-70b-8192".
        temperature (float): The temperature for the model. Defaults to 0.2.

    Returns:
        ChatGroq: The initialized Groq LLM instance of ChatGroq from Langchain integration.

    Raises:
        ValueError: If the Groq API key is not set in the environment variables.
    """

    # Get the API key from settings. ChatGroq expects a SecretStr type for the API key.
    groq_api_key: SecretStr | None = settings.GROQ_API_KEY
    if groq_api_key is None:
        raise ValueError(
            "Groq API key is not set in the environment variables. Check your environment variables"
        )

    # Map the model number to the actual model name
    model_mapping = {
        1: "llama3-70b-8192",
        2: "deepseek-r1-distill-llama-70b",
        3: "meta-llama/llama-4-scout-17b-16e-instruct",
    }

    # Initialize the Groq LLM with the specified model name
    groq_llm = ChatGroq(
        model=model_mapping.get(model_name, "llama3-70b-8192"),
        temperature=temperature,
        api_key=groq_api_key,
    )

    return groq_llm


# Tavily Web Search
def get_tavily_client(return_async: bool = False) -> TavilyClient | AsyncTavilyClient:
    """
    Initialize the Tavily Web Search client.
    \nPython SDK documentation: https://docs.tavily.com/sdk/python/reference

    Args:
        return_async (bool): If True, returns an asynchronous client. Defaults to False.

    Returns:
        TavilyClient | AsyncTavilyClient: The initialized Tavily client.
    """

    # Get the API key from settings
    tavily_api_key: str | None = get_key(api_key=settings.TAVILY_API_KEY)
    if tavily_api_key is None:
        raise ValueError(
            "Tavily API key is not set in the environment variables. Check your environment variables"
        )

    # Initialize the Tavily client
    if return_async:
        return AsyncTavilyClient(api_key=tavily_api_key)
    else:
        return TavilyClient(api_key=tavily_api_key)


# Exa Web Search
def get_exa_client(return_async: bool = False) -> Exa | AsyncExa:
    """
    Initialize the Exa Web Search client.
    \nPython SDK documentation: https://docs.exa.ai/sdks/python-sdk-specification

    Args:
        return_async (bool): If True, returns an asynchronous client. Defaults to False.

    Returns:
        Exa | AsyncExa: The initialized Exa client.
    """

    # Get the API key from settings
    exa_api_key: str | None = get_key(api_key=settings.EXA_API_KEY)
    if exa_api_key is None:
        raise ValueError(
            "Exa API key is not set in the environment variables. Check your environment variables"
        )

    # Initialize the Exa client
    if return_async:
        return AsyncExa(api_key=exa_api_key)
    else:
        return Exa(api_key=exa_api_key)


# these models support "json_schema" method for .with_structured_output(). Update these if you add new models that support this.
MODELS_SUPPORTING_JSON_SCHEMA: set[Callable[..., Any]] = {
    get_openai_model,
    get_mistral_model,
}


# This function helps to define different models for different nodes in the graph. I know this may seem a little too much but trust me its worth it.
def initialize_model_with_fallbacks(
    primary_model_fn: Callable[..., Any],
    primary_model_kwargs: dict,
    fallback_model_fns: list[Callable[..., Any]] | None = None,
    fallback_model_kwargs_list: list[dict] | None = None,
    structured_output_schema: type[BaseModel] | None = None,
    bind_tools: bool = False,
    tools: list[Any] | None = None,
    tool_choice: Any | None = None,
) -> ChatModel:
    """
    Initializes a primary model with optional structured output and tool binding,
    and sets up fallback models with the same options.

    Assumes model functions are defined in this file above like get_gemini_model, get_groq_model etc.
    Also assumes they have with_structured_output and bind_tools methods (I don't think we will use models where this assumption is not true).

    Waring: Make sure you are passing the correct model functions and kwargs. There is no type safety for this.

    Args:
        primary_model_fn (Callable[..., Any]): Function to initialize the primary model.
        primary_model_kwargs (dict): Keyword arguments for the primary model.
        fallback_model_fns (Optional[Sequence[Callable[..., Any]]]): Functions to initialize fallback models.
        fallback_model_kwargs_list (Optional[Sequence[dict]]): List of keyword arguments for each fallback model.
        structured_output_schema (Optional[Any]): Schema for structured output. If supplied method used for structured output is "json_schema". If None, structured output is not applied.
        bind_tools (bool): Whether to bind tools to the models.
        tools (Optional[list[Any]]): List of tools to bind if bind_tools is True.
        tool_choice (Any | None): Tool choice to use for the models. Use this to force a specific tool choice in which case give the name of tool.

    Returns:
        Any: The initialized model with fallbacks.

    Raises:
        ValueError: If fallback_model_fns and fallback_model_kwargs_list lengths do not match.
        Exception: If model initialization fails.

    Example:
        >>> from src.utils.models_initializer import get_gemini_model, get_groq_model, initialize_model_with_fallbacks
        >>> from src.agents.keywords_agent.schemas import Entities
        >>>
        >>> model = initialize_model_with_fallbacks(
        ...     primary_model_fn=get_gemini_model,
        ...     primary_model_kwargs={"model_name": 2, "temperature": 0.6},
        ...     fallback_model_fns=[get_groq_model, get_gemini_model],
        ...     fallback_model_kwargs_list=[
        ...         {"model_name": 1, "temperature": 0.6},
        ...         {"model_name": 3, "temperature": 0.6}
        ...     ],
        ...     structured_output_schema=Entities,
        ... )
    """
    # Initialize the primary model with explicit parameters
    primary_model = primary_model_fn(**primary_model_kwargs)

    # If a structured output schema is provided, apply it with the correct method
    if structured_output_schema is not None:
        if primary_model_fn in MODELS_SUPPORTING_JSON_SCHEMA:
            # Only add method="json_schema" for supported models
            primary_model = primary_model.with_structured_output(
                schema=structured_output_schema, method="json_schema"
            )
        else:
            # For other models, call without method parameter (default is usually structured output using function_calling)
            primary_model = primary_model.with_structured_output(
                schema=structured_output_schema
            )

    if bind_tools and tools is not None:
        # If tool_choice is provided add that parameter too
        if tool_choice is not None:
            primary_model = primary_model.bind_tools(
                tools=tools, tool_choice=tool_choice
            )
        else:
            primary_model = primary_model.bind_tools(tools=tools)

    # Initialize fallback models if provided
    fallbacks = []
    if fallback_model_fns and fallback_model_kwargs_list:

        if len(fallback_model_fns) != len(fallback_model_kwargs_list):
            raise ValueError(
                "fallback_model_fns and fallback_model_kwargs_list must have the same length."
            )

        for fn, kwargs in zip(fallback_model_fns, fallback_model_kwargs_list):
            fallback = fn(**kwargs)
            if structured_output_schema is not None:
                if fn in MODELS_SUPPORTING_JSON_SCHEMA:
                    # Only add method="json_schema" for supported models
                    fallback = fallback.with_structured_output(
                        schema=structured_output_schema, method="json_schema"
                    )
                else:
                    # For other models, call without method parameter (default is usually structured output using function_calling)
                    fallback = fallback.with_structured_output(
                        schema=structured_output_schema
                    )
            if bind_tools and tools is not None:
                if tool_choice is not None:
                    fallback = fallback.bind_tools(tools=tools, tool_choice=tool_choice)
                else:
                    fallback = fallback.bind_tools(tools=tools)
            fallbacks.append(fallback)

    # Attach fallbacks to the primary model
    if fallbacks:
        primary_model = primary_model.with_fallbacks(
            fallbacks=fallbacks,
        )

    return primary_model
