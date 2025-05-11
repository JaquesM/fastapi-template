from fastapi import APIRouter

from app.api.v1.routes import auth, users, contact

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(contact.router, prefix="/contact", tags=["contact"])
