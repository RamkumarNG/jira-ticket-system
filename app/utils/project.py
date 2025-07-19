import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database.models import ProjectTable

async def check_project_exists(project_name: str, db: AsyncSession):
    stm = select(ProjectTable).where(ProjectTable.name == project_name)
    result = await db.execute(stm)
    project = result.scalar_one_or_none()

    return project

async def create_default_project(db: AsyncSession, project_name: str = "default_project") -> ProjectTable:
    stmt = select(ProjectTable).where(ProjectTable.name == project_name)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()

    if project:
        return project

    new_project = ProjectTable(
        project_id=uuid.uuid4(),
        name=project_name
    )
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    return new_project
