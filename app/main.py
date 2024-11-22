import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router

# %if app_type == portal
from app.api.auth import router as auth_router

# %endif
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app = FastAPI()

# Add middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api", tags=["API"])
# %if app_type == portal
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
# %endif


@app.get("/")
async def root():
    return {"message": "Welcome to Cobo WaaS 2 Demo !!"}


# Add this line to print the environment at startup
print(f"Starting application with COBO_ENV: {settings.COBO_ENV}")
