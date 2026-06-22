from pydantic_settings import BaseSettings
from typing import Optional
class Settings(BaseSettings):
    """应用配置"""
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    amap_api_key: str = ""
    llm_model: str = "mimo-v2.5-pro"
    amap_js_key: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
_settings: Optional[Settings] = None
def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings