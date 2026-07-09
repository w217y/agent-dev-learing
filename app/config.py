from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    openai_model: str = "gpt-5.5"
    openai_api_base_url: str = "http://127.0.0.1:8080"

    class Config:
        env_file = ".env"

settings = Settings()