from fastapi import Depends, HTTPException, status
from app.auth.dependencies import get_current_user
from app.projects.dao import ProjectsDAO
from sqlalchemy.ext.asyncio import AsyncSession
from app.dao.session_maker import SessionDep


# Зависимость для получения владельца проекта
async def get_project_owner(
        project_id: int,
        current_user=Depends(get_current_user),
        session: AsyncSession = Depends(SessionDep)  # Используем Depends для асинхронной сессии
):
    # Получаем проект из базы данных
    project = await ProjectsDAO.get_project(session, project_id)

    # Если проект не найден или владелец проекта не совпадает с текущим пользователем
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    return project
