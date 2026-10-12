from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.deps.auth import get_current_super_admin

from app.api.routers import (
    college, department, faculty_member, announcement, event,
    academic_resource, timetable, gallery_album, gallery_image,
    academic_calendar, help_center_article, setting, audit_log,
    role, permission, department_administrator, super_administrator,
    auth
)

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Starting {settings.APP_NAME}...")
    yield
    print(f"Shutting down {settings.APP_NAME}...")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Register all routers
app.include_router(auth.router)
app.include_router(college.router, dependencies=[Depends(get_current_super_admin)])
app.include_router(department.router)
app.include_router(faculty_member.router)
app.include_router(announcement.router, dependencies=[Depends(get_current_super_admin)])
app.include_router(event.router, dependencies=[Depends(get_current_super_admin)])
app.include_router(academic_resource.router, dependencies=[Depends(get_current_super_admin)])
app.include_router(timetable.router, dependencies=[Depends(get_current_super_admin)])
app.include_router(gallery_album.router, dependencies=[Depends(get_current_super_admin)])
app.include_router(gallery_image.router, dependencies=[Depends(get_current_super_admin)])
app.include_router(academic_calendar.router, dependencies=[Depends(get_current_super_admin)])
app.include_router(help_center_article.router, dependencies=[Depends(get_current_super_admin)])
app.include_router(setting.router, dependencies=[Depends(get_current_super_admin)])
app.include_router(audit_log.router, dependencies=[Depends(get_current_super_admin)])
app.include_router(role.router, dependencies=[Depends(get_current_super_admin)])
app.include_router(permission.router, dependencies=[Depends(get_current_super_admin)])
app.include_router(department_administrator.router, dependencies=[Depends(get_current_super_admin)])
app.include_router(super_administrator.router, dependencies=[Depends(get_current_super_admin)])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.APP_NAME}
