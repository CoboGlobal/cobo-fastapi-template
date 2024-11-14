import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

print(f"Current COBO_ENV: {os.getenv('COBO_ENV')}")


class Settings:
    COBO_API_KEY: str = os.getenv("COBO_API_KEY", "")
    COBO_API_SECRET: str = os.getenv("COBO_API_SECRET", "")
    COBO_ENV: str = os.getenv("COBO_ENV", "development")


settings = Settings()
