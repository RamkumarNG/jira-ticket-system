from pathlib import Path
from dotenv import load_dotenv

from pydantic import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    VERSION: str = "v1"
    DATABASE_URL: str
    # SECRET_KEY: str

    class Config:
        env_file = Path(__file__).resolve().parent.parent / ".env"
        env_file_encoding = "utf-8"

settings = Settings()