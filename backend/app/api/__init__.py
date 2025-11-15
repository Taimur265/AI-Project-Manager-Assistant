from fastapi import APIRouter
from .auth import router as auth_router
from .projects import router as projects_router
from .tasks import router as tasks_router
from .reports import router as reports_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(projects_router, prefix="/projects", tags=["projects"])
api_router.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
api_router.include_router(reports_router, prefix="/reports", tags=["reports"])
