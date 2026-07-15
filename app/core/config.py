from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Ye class saari settings ko ek jagah rakhti hai.
    Values .env file se aayengi.
    """

    # App ka naam
    APP_NAME: str = "AI Resume Analyzer"
    APP_VERSION: str = "2.0"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "dev-only-secret-key-do-not-use-in-production"

    # Database
    DATABASE_URL: str = "sqlite:///./resume_analyzer.db"

    # File Uploads
    UPLOAD_DIR: str = "app/uploads"
    MAX_UPLOAD_SIZE_MB: int = 5

    # ----------------------------
    # Email (SMTP)
    # ----------------------------
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_EMAIL: str = ""
    SMTP_PASSWORD: str = ""
    RECEIVER_EMAIL: str = ""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Ye ek hi baar banega, poore project mein yahi use hoga
settings = Settings()