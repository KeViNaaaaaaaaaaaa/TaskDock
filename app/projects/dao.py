from operator import and_
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException, status

from app.auth.models import User
from app.dao.database import engine
from app.projects.models import Project, ProjectMembership, Task

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
    async def get_project_owner(session: AsyncSession, project_id: int) -> Project:
        # Получение проекта по ID
        result = await session.execute(select(Project).where(Project.id == project_id))
        project = result.scalars().first()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        result = await session.execute(
            select(ProjectMembership.user_id).where(
                ProjectMembership.project_id == project.id and ProjectMembership.user_id == 'CREATOR'))
        project_user_id = result.scalars().first()

        if not project_user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="fsdfdsfdssdsdv"
            )

        return project_user_id

    # @staticmethod
    # async def get_projects(session: AsyncSession, project_id: int) -> Project:
    #     # Получение проекта по ID
    #     result = await session.execute(select(Project).where(Project.id == project_id))
    #     projects = result.scalars().all()
    #
    #     if not projects:
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND,
    #             detail="Project not found"
    #         )
    #     return projects

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

    @staticmethod
    async def get_user_projects(session: AsyncSession, user_id: int) -> List[Project]:
        # Получение всех проектов, где пользователь является участником
        result = await session.execute(
            select(Project).join(ProjectMembership).filter(ProjectMembership.user_id == user_id)
        )
        projects = result.scalars().all()

        # Проверка, если проектов нет
        if not projects:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Projects not found"
            )

        return projects

    @staticmethod
    async def get_users_projects(session: AsyncSession, user_id: int) -> List[Project]:
        # Получение всех проектов, где пользователь является участником
        result = await session.execute(
            select(Project).join(ProjectMembership).filter(ProjectMembership.user_id == user_id)
        )
        projects = result.scalars().all()

        # Проверка, если проектов нет
        if not projects:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Projects not found"
            )
        r = []
        print(len(projects))
        for project in projects:
            result_members = await session.execute(
                select(User).join(ProjectMembership).filter(
                    and_(
                        and_(
                            ProjectMembership.project_id == project.id,
                            ProjectMembership.role == 'MEMBER'
                        ),
                        User.id == ProjectMembership.user_id)
                ))
            projects_members = result_members.scalars().all()
            r.append(projects_members)
        print(r)
        return r

    @staticmethod
    async def get_project_tasks(session: AsyncSession, project_id: int) -> List[Project]:
        result_members = await session.execute(select(Task).filter(Task.project_id == project_id))
        projects_members = result_members.scalars().all()

        return projects_members

    @staticmethod
    async def get_projects_tasks(session: AsyncSession, user_id: int) -> List[Project]:
        result = await session.execute(
            select(Project).join(ProjectMembership).filter(ProjectMembership.user_id == user_id)
        )
        projects = result.scalars().all()

        # Проверка, если проектов нет
        if not projects:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Projects not found"
            )
        r = []
        print(len(projects))
        for project in projects:
            result_members = await session.execute(
                select(Task).filter(Task.project_id == project.id))
            projects_members = result_members.scalars().all()
            r.append(projects_members)
        print(r)
        return r

    @staticmethod
    async def get_users_owner(session: AsyncSession, user_id: int) -> List[Project]:
        # Получение всех проектов, где пользователь является участником
        result = await session.execute(
            select(Project).join(ProjectMembership).filter(ProjectMembership.user_id == user_id)
        )
        projects = result.scalars().all()

        # Проверка, если проектов нет
        if not projects:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Projects not found"
            )
        r = []
        print(len(projects))
        for project in projects:
            result_members = await session.execute(
                select(User.nickname).join(ProjectMembership).filter(
                    and_(
                        and_(
                            ProjectMembership.project_id == project.id,
                            ProjectMembership.role == 'CREATOR'
                        ),
                        User.id == ProjectMembership.user_id)
                ))
            projects_members = result_members.scalars().all()
            r.append(projects_members)
        print(r)
        return r
