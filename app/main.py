from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.main import api_router

def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


# Main app
app = FastAPI(
    title="Fastapi Template",
    version="1.0.0",
    generate_unique_id_function=custom_generate_unique_id,
    redirect_slashes=True,
)

# Middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # [settings.FRONTEND_HOST],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routes
app.include_router(api_router, prefix="/v1")

