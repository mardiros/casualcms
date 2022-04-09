from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    template_search_path: str = Field(...)

    class Config:
        env_prefix = "casualcms_"
