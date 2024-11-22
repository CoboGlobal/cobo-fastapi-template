import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

print(f"Current COBO_ENV: {os.getenv('COBO_ENV')}")


class Settings:
    # %if app_type == portal
    SECRET_KEY = os.getenv("SECRET_KEY", "")
    COBO_APP_SECRET: str = os.getenv("COBO_APP_SECRET", "")
    COBO_APP_CLIENT_ID: str = os.getenv("COBO_APP_CLIENT_ID", "")
    # %else
    COBO_API_SECRET: str = os.getenv("COBO_API_SECRET", "")
    # %endif
    COBO_ENV: str = os.getenv("COBO_ENV", "dev")

    @property
    def api_host(self) -> str:
        if self.COBO_ENV == "sandbox":
            return "https://api.sandbox.cobo.com/v2"
        if self.COBO_ENV == "prod":
            return "https://api.cobo.com/v2"
        return "https://api.dev.cobo.com/v2"

    # %if app_type == portal
    @property
    def jks_url(self) -> str:
        if self.COBO_ENV == "sandbox":
            return "https://api.sandbox.cobo.com/web/v2/oauth/authorize/jwks.json"
        if self.COBO_ENV == "prod":
            return "https://api.cobo.com/web/v2/oauth/authorize/jwks.json"
        return "https://api.dev.cobo.com/web/v2/oauth/authorize/jwks.json"

    # %endif


settings = Settings()
