from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from dotenv import find_dotenv


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    This class uses pydantic-settings to load and validate sensitive API keys and configuration
    values from a .env file or environment variables. All API keys are stored as SecretStr for security.

    **Attributes:**

    **LLMs:**
        GEMINI_API_KEY (SecretStr | None): API key for Gemini service.
        GROQ_API_KEY (SecretStr | None): API key for Groq service.

    **Web Search APIs:**
        TAVILY_API_KEY (SecretStr | None): API key for Tavily service.
        EXA_API_KEY (SecretStr | None): API key for Exa service.

    **Observability and Monitoring:**
        OPIK_API_KEY (SecretStr | None): API key for Opik service.
        OPIK_WORKSPACE (str | None): Workspace identifier for Opik.
        OPIK_PROJECT_NAME (str | None): Project name for Opik.

    **Server Configuration:**
        HOST (str): Host address for FastAPI server. Defaults to "0.0.0.0".
        PORT (int): Port for FastAPI server. Defaults to 8000.

    **Example Usage:**
        ```python
        from src.utils.settings import settings, get_api_key

        # Accessing API keys
        gemini_key = get_api_key(api_key=settings.GEMINI_API_KEY)

        # Accessing server configuration
        host = settings.HOST
        port = settings.PORT
        ```
    """

    # Configuration for loading environment variables
    model_config = SettingsConfigDict(
        env_file=find_dotenv(),  # Automatically find and use the .env file
        env_file_encoding="utf-8",
        env_ignore_empty=True,
    )

    # **API keys and configuration values**

    # LLMs
    GEMINI_API_KEY: SecretStr | None = None
    GROQ_API_KEY: SecretStr | None = None

    # Web Search APIs
    TAVILY_API_KEY: SecretStr | None = None
    EXA_API_KEY: SecretStr | None = None

    # Observability and Monitoring
    OPIK_API_KEY: SecretStr | None = None
    OPIK_WORKSPACE: str | None = None
    OPIK_PROJECT_NAME: str | None = None

    # FastAPI host and port with default values
    HOST: str = "0.0.0.0"
    PORT: int = 8000


# *******************************************************
# Singleton instance to be used throughout the application
# *******************************************************
settings = Settings()


def get_api_key(api_key: SecretStr | None) -> str | None:
    """
    Safely retrieve the value of a SecretStr API key.
    If env variable is declared but not set, it will return None.

    Args:
        api_key (SecretStr | None): The SecretStr API key object.

    Returns:
        (str | None): The actual API key string, or None if not set.

    Raises:
        ValueError: If the API key is not set or if there is an error retrieving it.
    """
    if api_key is not None:
        try:
            return api_key.get_secret_value()
        except Exception as exc:
            # Handle any error that may occur when retrieving the secret value
            raise ValueError(f"Failed to retrieve API key ({api_key}): {exc}") from exc
    else:
        # If the API key is None, return None
        return None