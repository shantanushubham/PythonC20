# import os
# from functools import lru_cache

# from dotenv import load_dotenv

# load_dotenv()


# class Settings:
#     postgres_user: str = os.getenv("POSTGRES_USER", "postgres")
#     postgres_password: str = os.getenv("POSTGRES_PASSWORD", "postgres")
#     postgres_db: str = os.getenv("POSTGRES_DB", "fast_task_app")
#     postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
#     postgres_port: str = os.getenv("POSTGRES_PORT", "5432")

#     @property
#     def database_url(self) -> str:
#         explicit_url = os.getenv("DATABASE_URL")
#         if explicit_url and "${" not in explicit_url:
#             return explicit_url

#         return (
#             f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
#             f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
#         )


# @lru_cache
# def get_settings() -> Settings:
#     return Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    
    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()

