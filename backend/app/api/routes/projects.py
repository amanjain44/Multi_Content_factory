from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.services.project_service import ProjectService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(project_in: ProjectCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = ProjectService(db, current_user.id)
    return await service.create_project(project_in)

@router.get("", response_model=List[ProjectResponse])
async def read_projects(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = ProjectService(db, current_user.id)
    return await service.get_projects(skip=skip, limit=limit)

@router.get("/{project_id}", response_model=ProjectResponse)
async def read_project(project_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = ProjectService(db, current_user.id)
    return await service.get_project(project_id)

@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: UUID, project_in: ProjectUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = ProjectService(db, current_user.id)
    return await service.update_project(project_id, project_in)

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = ProjectService(db, current_user.id)
    await service.delete_project(project_id)
    return None
