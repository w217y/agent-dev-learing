from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    # Chat LLM 配置
    openai_api_key: str
    openai_model: str = "gpt-5.5"
    openai_api_base_url: str = "http://127.0.0.1:8080"

    # Embedding 配置
    embedding_provider: str = "local"
    embedding_model: str = "BAAI/bge-small-zh-v1.5"
    embedding_dim: str = 512

    # Database / RAG 配置
    database_url: str
    upload_dir: str = "data/uploads"
    top_k: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()