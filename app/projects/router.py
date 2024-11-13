from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.auth.models import User
from app.projects.models import Project, ProjectMembership, ProjectRole
from app.projects.dependencies import get_current_user
from app.projects.dao import get_db
from app.projects.schemas import ProjectCreate
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

    db.delete(membership)
    await db.commit()
    return {"message": "Участник удален успешно"}
