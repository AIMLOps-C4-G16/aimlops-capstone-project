from typing import List

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings

from models import ICModel, ImageDatabaseIndex


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"

    # BACKEND_CORS_ORIGINS is a comma-separated list of origins
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # type: ignore
        "http://localhost:8000",  # type: ignore
        "https://localhost:3000",  # type: ignore
        "https://localhost:8000",  # type: ignore
    ]

    PROJECT_NAME: str = "Image Captioning Model and Image Database Indexing API"

    TEMPLATES_DIRECTORY: str = "templates"

    IC_MODEL: List[ICModel] = []

    IMAGE_DB_INDEX: List[ImageDatabaseIndex] = []

    class Config:
        case_sensitive = True

settings = Settings()
