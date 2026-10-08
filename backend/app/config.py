from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CyGRC SOC API"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/cygrc_soc"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
