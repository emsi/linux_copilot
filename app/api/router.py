"""Main router for API."""
from fastapi import APIRouter

from app.api.commands_router import commands_router

api_router = APIRouter()
api_router.include_router(commands_router, prefix="/commands", tags=["commands"])
