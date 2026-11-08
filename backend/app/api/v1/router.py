"""V1 API Router aggregating auth, vehicles, and health endpoints."""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.api.v1.map import router as map_router
from app.api.v1.regulations import router as regulations_router
from app.api.v1.vehicles import router as vehicles_router

api_v1_router = APIRouter(prefix="/v1")

# Mount sub-routers
api_v1_router.include_router(auth_router)
api_v1_router.include_router(vehicles_router)
api_v1_router.include_router(regulations_router)
api_v1_router.include_router(map_router)
api_v1_router.include_router(health_router)
