from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from app.auth.models import User
from app.dao.session_maker import SessionDep
from app.projects.models import Project, ProjectMembership, ProjectRole, Task
from app.projects.dependencies import get_current_user
from app.projects.dao import get_db, ProjectsDAO
from app.projects.schemas import ProjectCreate, ProjectRead, ProjectDelete, TaskCreate
from sqlalchemy.future import select

router = APIRouter()


@router.post("/projects/")
async def create_project(
        project: ProjectCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    new_project = Project(
        title=project.title,
        description=project.description,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)

    membership = ProjectMembership(
        project_id=new_project.id,
        user_id=current_user.id,
        role=ProjectRole.CREATOR
    )
    db.add(membership)
    await db.commit()

    return {"message": "Проект успешно создан", "project_id": new_project.id}


@router.delete("/projects/delete")
async def delete_project(
        project_id: int,
        project_title: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    res = await db.execute(select(Project).filter(Project.id == project_id))
    project = res.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    res = await db.execute(select(ProjectMembership).filter_by(
        project_id=project_id, user_id=current_user.id, role=ProjectRole.CREATOR
    ))
    cheto3 = res.scalars().first()
    if not cheto3:
        raise HTTPException(status_code=403, detail="Только создатель проекта может удалять участников")
    res = await db.execute(select(ProjectMembership).filter_by(
        project_id=project_id
    ))
    cheto4 = res.scalars().first()
    await db.delete(cheto4)
    await db.delete(project)
    await db.commit()
    return {"message": "Участник удален успешно"}

    # new_project = Project(
    #     title=project.title,
    #     description=project.description,
    #     created_at=datetime.utcnow(),
    #     updated_at=datetime.utcnow(),
    # )
    # db.delete(new_project)
    # await db.commit()
    # await db.refresh(new_project)
    #
    # membership = ProjectMembership(
    #     project_id=new_project.id,
    #     user_id=current_user.id,
    #     role=ProjectRole.CREATOR
    # )
    # db.delete(membership)
    # await db.commit()
    #
    # return {"message": "Проект успешно удален", "project_id": new_project.id}


# @router.get("/projectss/", response_model=None)
# async def get_me(project: Depends(get_user_projects)):
#     return ProjectRead.model_validate(project)


@router.post("/projects/{project_id}/members")
async def add_member(
        project_id: int,
        user_nickname: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    res = await db.execute(select(Project).filter(Project.id == project_id))
    project = res.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")

    res = await db.execute(select(ProjectMembership).filter_by(
        project_id=project_id, user_id=current_user.id, role=ProjectRole.CREATOR))
    cheto = res.scalars().first()
    if not cheto:
        raise HTTPException(status_code=403, detail="Только создатель проекта может добавлять участников")

    res = await db.execute(select(User).filter(User.nickname == user_nickname))
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    res = await db.execute(select(ProjectMembership).filter_by(project_id=project_id, user_id=user.id))
    cheto1 = res.scalars().first()
    if cheto1:
        raise HTTPException(status_code=400, detail="Пользователь уже является участником")

    membership = ProjectMembership(project_id=project_id, user_id=user.id, role=ProjectRole.MEMBER)
    db.add(membership)
    await db.commit()
    return {"message": "Участник добавлен успешно"}


@router.delete("/projects/{project_id}/members/{user_nickname}")
async def remove_member(
        project_id: int,
        user_nickname: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    res = await db.execute(select(Project).filter(Project.id == project_id))
    project = res.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    res = await db.execute(select(ProjectMembership).filter_by(
        project_id=project_id, user_id=current_user.id, role=ProjectRole.CREATOR
    ))
    cheto3 = res.scalars().first()
    if not cheto3:
        raise HTTPException(status_code=403, detail="Только создатель проекта может удалять участников")

    res = await db.execute(select(User).filter(User.nickname == user_nickname))
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    res = await db.execute(select(ProjectMembership).filter_by(project_id=project_id, user_id=user.id))
    membership = res.scalars().first()
    if not membership:
        raise HTTPException(status_code=404, detail="Участник не найден")

    await db.delete(membership)
    await db.commit()
    return {"message": "Участник удален успешно"}


@router.post("/projects/{project_id}/tasks")
async def create_project(
        task: TaskCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    new_task = Task(
        title=task.title,
        description=task.description,
        project_id=task.project_id,
        assignee_id=task.assignee_id,
        status=task.status,
        priority=task.priority,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        due_data=task.due_date,
        tester_id=task.tester_id,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)

    return {"message": "Проект успешно создан", "project_id": new_task.project_id}
