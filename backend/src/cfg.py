from pydantic_settings import BaseSettings, SettingsConfigDict

from pydantic import (
    Field,
    PostgresDsn,
)


class Settings(BaseSettings):
    # Redundant, but just so we know...
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8')

    pg_connection_uri: str = "postgres://user:pass@localhost:5432/finance"
    

settings = Settings()
