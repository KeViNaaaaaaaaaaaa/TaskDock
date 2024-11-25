from fastapi import Depends, HTTPException, status
from app.auth.dependencies import get_current_user
from app.auth.models import User
from backend.app.projects import ProjectsDAO
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.dao.session_maker import SessionDep
from backend.app.projects import Project


# Зависимость для получения владельца проекта
async def get_project_owner(
        project_id: int,
        current_user=Depends(get_current_user),
        session: AsyncSession = SessionDep  # Используем Depends для асинхронной сессии
):
    # Получаем проект из базы данных
    project = await ProjectsDAO.get_project(session, project_id)

    # Если проект не найден или владелец проекта не совпадает с текущим пользователем
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    user_id = await ProjectsDAO.get_project_owner(session, project_id)

    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не владелец проекта"
        )

    return user_id


async def get_user_projects(
        current_user: User = Depends(get_current_user),
        session: AsyncSession = SessionDep
) -> Project:
    # Получаем все проекты, в которых участвует пользователь
    projects = await ProjectsDAO.get_user_projects(session, current_user.id)

    if not projects:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No projects found for the user")

    return projects


async def get_project(
        project_id: int,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = SessionDep
) -> Project:
    # Получаем все проекты, в которых участвует пользователь
    projects = await ProjectsDAO.get_project(session, project_id)

    if not projects:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No projects found for the user")

    return projects

    # return [
    #     ProjectPublic(
    #         id=project.id,
    #         title=project.title,
    #         description=project.description,
    #         created_at=project.created_at,
    #         updated_at=project.updated_at,
    #         status=project.status or "ACTIVE",  # Статус по умолчанию
    #         members=[
    #             ProjectMembershipBase(
    #                 nickname=member.nickname,
    #                 first_name=member.first_name,
    #                 last_name=member.last_name
    #             )
    #             for member in project.members
    #         ]
    #     )
    #     for project in projects
    # ]


async def get_users_projects(
        current_user: User = Depends(get_current_user),
        session: AsyncSession = SessionDep
) -> User:
    projects_members = await ProjectsDAO.get_users_projects(session, current_user.id)

    if not projects_members:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No projects found for the user")

    return projects_members


async def get_users_owner(
        current_user: User = Depends(get_current_user),
        session: AsyncSession = SessionDep
) -> User:
    projects_members = await ProjectsDAO.get_users_owner(session, current_user.id)

    if not projects_members:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No projects found for the user")

    return projects_members


async def get_projects_tasks(
        user_id: int,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = SessionDep,
) -> User:
    projects_members = await ProjectsDAO.get_projects_tasks(session, user_id)

    if not projects_members:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No projects found for the user")

    return projects_members


async def get_project_tasks(
        current_user: User = Depends(get_current_user),
        session: AsyncSession = SessionDep
) -> User:
    projects_members = await ProjectsDAO.get_project_tasks(session, current_user.id)

    if not projects_members:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No projects found for the user")

    return projects_members
