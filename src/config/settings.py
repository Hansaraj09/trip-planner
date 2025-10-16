import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    google_api_key: str = Field(default="", validation_alias="GOOGLE_API_KEY")
    openweather_api_key: str = Field(default="", validation_alias="OPENWEATHER_API_KEY")
    amadeus_api_key: str = Field(default="", validation_alias="AMADEUS_API_KEY")
    amadeus_api_secret: str = Field(default="", validation_alias="AMADEUS_API_SECRET")
    
    # LangSmith Configuration
    langsmith_api_key: str = Field(default="", validation_alias="LANGSMITH_API_KEY")
    langchain_tracing_v2: bool = Field(default=False, validation_alias="LANGCHAIN_TRACING_V2")
    langchain_project: str = Field(default="trip-planner-agent", validation_alias="LANGCHAIN_PROJECT")
    
    # Application Settings
    debug: bool = Field(default=False, validation_alias="DEBUG")
    
    # API Endpoints
    openweather_base_url: str = "https://api.openweathermap.org/data/2.5"
    openweather_forecast_url: str = "https://api.openweathermap.org/data/2.5/forecast"
    
    # LLM Settings
    temperature: float = 0.7
    max_tokens: int = 2000
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # This allows extra env vars without errors
    )

# Global settings instance
settings = Settings()

# Set LangSmith environment variables if tracing is enabled
if settings.langchain_tracing_v2:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key
    os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project