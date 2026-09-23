from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import projects, workflow_stages, health, ai, sources, schedules, diagnostics, auth

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(projects.router, prefix=f"{settings.API_V1_STR}/projects", tags=["projects"])
app.include_router(sources.router, prefix=f"{settings.API_V1_STR}/projects", tags=["sources"])
app.include_router(workflow_stages.router, prefix=f"{settings.API_V1_STR}/projects", tags=["workflow_stages"])
app.include_router(ai.router, prefix=f"{settings.API_V1_STR}/ai", tags=["ai"])
app.include_router(schedules.router, prefix=f"{settings.API_V1_STR}/schedules", tags=["schedules"])
app.include_router(diagnostics.router, prefix=f"{settings.API_V1_STR}/diagnostics", tags=["diagnostics"])
