"""
here we initialize our langchain models and web search sdks so we can just import them in rest of our app.
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from tavily import (
    TavilyClient,
    AsyncTavilyClient,
)
from exa_py import Exa
from pydantic import SecretStr
from src.utils.settings import settings, get_api_key

# Gemini LLM
def get_gemini_model(model_name: str = "gemini-2.0-flash") -> ChatGoogleGenerativeAI:
    """
    Initialize the Gemini LLM with the specified model name.
    Available model names: 
    
    for latest available models: https://ai.google.dev/gemini-api/docs/models#model-variations
    
    - "gemini-2.0-flash"
    - "gemini-2.5-flash-preview-04-17"
    - "gemini-2.5-pro-exp-03-25"
    - "gemini-1.5-pro"
    
    Args:
        model_name (str): The name of the model to use. Defaults to "gemini-2.0-flash".
    
    Returns:
        ChatGoogleGenerativeAI: The initialized Gemini LLM instance of ChatGoogleGenerativeAI from Langchain integration.
    """

    # Get the API key from settings
    gemini_api_key: str | None = get_api_key(api_key=settings.GEMINI_API_KEY)
    if gemini_api_key is None:
        raise ValueError("Gemini API key is not set in the environment variables. Check your environment variables")

    # Initialize the Gemini LLM with the specified model name
    gemini_llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0.2,
        google_api_key=gemini_api_key,
        max_retries=2,
    )

    return gemini_llm

# Groq LLM
def get_groq_model(model_name: str = "llama3-70b-8192") -> ChatGroq:
    """
    Initialize the Groq LLM with the specified model name.
    
    Available model names:
    \nFor latest available models: https://console.groq.com/docs/models
    \nFor rate limits: https://console.groq.com/dashboard/limits

    - "llama3-70b-8192"
    - "deepseek-r1-distill-llama-70b"
    - "meta-llama/llama-4-scout-17b-16e-instruct"
    
    Args:
        model_name (str): The name of the model to use. Defaults to "llama3-70b-8192".
        
    Returns:
        ChatGroq: The initialized Groq LLM instance of ChatGroq from Lancgchain integration.
    """

    # Get the API key from settings. ChatGroq expects a SecretStr type for the API key so we import that directtly instead of using get_api_key function
    groq_api_key: SecretStr | None = settings.GROQ_API_KEY
    if groq_api_key is None:
        raise ValueError("Groq API key is not set in the environment variables. Check your environment variables")

    # Initialize the Groq LLM with the specified model name
    groq_llm = ChatGroq(
        model=model_name,
        temperature=0.2,
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
    tavily_api_key: str | None = get_api_key(api_key=settings.TAVILY_API_KEY)
    if tavily_api_key is None:
        raise ValueError("Tavily API key is not set in the environment variables. Check your environment variables")

    # Initialize the Tavily client
    if return_async:
        return AsyncTavilyClient(api_key=tavily_api_key)
    else:
        return TavilyClient(api_key=tavily_api_key)
    
# Exa Web Search
def get_exa_client() -> Exa:
    """
    Initialize the Exa Web Search client.
    \nPython SDK documentation: https://docs.exa.ai/sdks/python-sdk-specification
    
    Returns:
        Exa: The initialized Exa client.
    """

    # Get the API key from settings
    exa_api_key: str | None = get_api_key(api_key=settings.EXA_API_KEY)
    if exa_api_key is None:
        raise ValueError("Exa API key is not set in the environment variables. Check your environment variables")

    # Initialize the Exa client
    return Exa(api_key=exa_api_key)