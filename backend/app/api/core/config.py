from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        PROJECT_NAME: Project name.
        DATABASE_URL: Database connection URL.
        SECRET_KEY: Key for signing JWT tokens.
        JWT_ALGORITHM: JWT encryption algorithm.
        ACCESS_TOKEN_EXPIRE_MINUTES: Token expiration time in minutes.
    """

    PROJECT_NAME: str = "Paper Trading Simulator"
    DATABASE_URL: str
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()