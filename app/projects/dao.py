from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException, status

from app.dao.database import engine
from app.projects.models import Project

# Создаем сессию для работы с базой данных
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Зависимость для работы с базой данных в FastAPI
async def get_db() -> AsyncSession:
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()


class ProjectsDAO:
    @staticmethod
    async def create_project(session: AsyncSession, project_data: dict) -> Project:
        # Создание нового проекта
        project = Project(**project_data)
        session.add(project)
        await session.commit()
        await session.refresh(project)
        return project

    @staticmethod
    async def get_project(session: AsyncSession, project_id: int) -> Project:
        # Получение проекта по ID
        result = await session.execute(select(Project).where(Project.id == project_id))
        project = result.scalars().first()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        return project

    @staticmethod
    async def delete_project(session: AsyncSession, project_id: int) -> Project:
        # Удаление проекта
        result = await session.execute(select(Project).where(Project.id == project_id))
        project = result.scalars().first()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        await session.delete(project)
        await session.commit()
        return project

