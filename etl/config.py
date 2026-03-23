import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    db_host: str
    db_port: str
    db_name: str
    db_user: str
    db_password: str
    db_table_name: str
    db_schema: str
    coingecko_api_url: str
    
    model_config =  SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def db_connection_string(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
