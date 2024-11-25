from datetime import datetime
from operator import itemgetter
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from app.auth.models import User
from app.dao.session_maker import SessionDep
from app.projects.models import Project, ProjectMembership, ProjectRole, Task
from app.projects.dependencies import get_current_user, get_project_owner, get_user_projects, get_users_projects, \
    get_projects_tasks, get_users_owner, get_project, get_project_tasks
from app.projects.dao import get_db, ProjectsDAO
from app.projects.schemas import ProjectCreate, ProjectRead, ProjectDelete, TaskCreate, ProjectMembershipBase, \
    ProjectUpdate, TaskUpdate, TaskRead
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


@router.put("/projects/update")
async def update_project(
        project_id: int,
        project: ProjectUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    res = await db.execute(select(Project).filter_by(id=project_id))
    current_project = res.scalars().first()
    if not current_project:
        raise HTTPException(status_code=404, detail="Проект не найден")

    update_dict = project.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(current_project, key, value)

    db.add(current_project)
    await db.commit()
    await db.refresh(current_project)

    return {"message": "Проект успешно обновлен", "project_id": project_id}


# @router.put("/projects/update")
# async def update_project(
#         project_id: int,
#         project: ProjectUpdate,
#         db: Session = Depends(get_db),
#         project_info: List[Project] = Depends(get_project),
#         current_user: User = Depends(get_current_user),
# ):
#     current_project = await db.get(Project, project_id)
#     update_dict = project.model_dump(exclude_unset=True)
#     current_project.sqlmodel_update(update_dict)
#     db.add(current_project)
#     await db.commit()
#     await db.refresh(current_project)
#
#     return {"message": "Проект успешно обновлен", "project_id": project_id}


@router.delete("/projects/delete/")
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
        project_id=project_id, user_id=current_user.id, role='CREATOR'
    ))
    cheto3 = res.scalars().first()
    if not cheto3:
        raise HTTPException(status_code=403, detail="Только создатель проекта может его удалить")
    res = await db.execute(select(ProjectMembership).filter_by(
        project_id=project_id
    ))
    cheto4 = res.scalars().all()
    if cheto4:
        await db.delete(cheto4)
    res = await db.execute(select(Task).filter_by(
        project_id=project_id
    ))
    cheto5 = res.scalars().all()
    if cheto5:
        await db.delete(cheto5)
        await db.commit()

    # res = await db.execute(select(User).filter_by(
    #     role_id=1
    # ))
    # cheto6 = res.scalars().all()
    # if cheto5:
    #     await db.delete(cheto6)

    await db.delete(project)
    await db.commit()
    return {"message": "Проект удален успешно"}


@router.get("/projectss/")
async def get_me(projects: List[Project] = Depends(get_user_projects),
                 members: List[List[User]] = Depends(get_users_projects),
                 tasks: List[List[Task]] = Depends(get_projects_tasks),
                 owner: List[List[User]] = Depends(get_users_owner)):
    a = [
        ProjectRead(
            id=project.id,
            owner=[own for own in owner[projects.index(project)]][0],
            title=project.title,
            description=project.description,
            created_at=project.created_at,
            updated_at=project.updated_at,
            status=project.status,
            members=[
                f"{member.nickname} ({member.first_name} {member.last_name})"
                for member in members[projects.index(project)]
            ] if members[projects.index(project)] else [],
            tasks=[
                f"{task.title} ({task.description} {task.status})"
                for task in tasks[projects.index(project)]
            ] if tasks[projects.index(project)] else [],
        )
        for project in projects

    ]

    return a


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
async def create_tasks(
        task: TaskCreate,
        project_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        current_project_user: Task = Depends(get_project_owner),
):
    new_task = Task(
        title=task.title,
        description=task.description,
        project_id=project_id,
        assignee_id=current_user.id,
        status=task.status,
        priority=task.priority,
        tester_id=task.tester_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        # due_data=due_date,
    )
    if current_user.id != current_project_user:
        raise HTTPException(status_code=403, detail="Только создатель проекта может добавлять задачи")
    # if task.tester_id == current_user.id:
    #     raise HTTPException(status_code=403, detail="Создатель не может быть тестером")
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

    return {"message": "Задача успешно создана", "project_id": new_task.project_id}


@router.delete("/projects/{project_id}/tasks")
async def delete_tasks(
        project_id: int,
        task_title: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        current_project_user: Task = Depends(get_project_owner),
):
    if current_user.id != current_project_user:
        raise HTTPException(status_code=403, detail="Только создатель проекта может удалить задачу")

    res = await db.execute(select(Task).filter_by(
        project_id=project_id, title=task_title
    ))
    cheto5 = res.scalars().first()

    await db.delete(cheto5)
    await db.commit()

    return {"message": "Проект успешно удален", "project_id": project_id}


@router.put("/projects/{project_id}/tasks")
async def update_project(
        title: str,
        project_id: int,
        task: TaskUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        projects: List[Project] = Depends(get_user_projects),
):
    res = await db.execute(select(Task).filter_by(project_id=project_id, title=title))
    membership = res.scalars().first()
    print(membership)
    if not membership:
        raise HTTPException(status_code=404, detail="Проект не найден")

    update_dict = task.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(membership, key, value)

    db.add(membership)
    await db.commit()
    await db.refresh(membership)

    return {"message": "Таска успешно обновлена", "title": title}


@router.get("/projects/tasks")
async def get_me(project_id: int,
                 tasks: List[Task] = Depends(get_project_tasks)):
    a = [
        TaskRead(
            id=task.id,
            title=task.title,
            priority=task.priority,
            created_at=task.created_at,
            updated_at=task.updated_at,
            project_id=project_id,
            status=task.status,
            assignee_id=task.assignee_id,
            tester_id=task.tester_id,
        )
        for task in tasks

    ]

    return a


@router.put("/projects/{project_id}/members")
async def update_members(
        title: str,
        project_id: int,
        task: TaskUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        projects: List[Project] = Depends(get_user_projects),
):
    res = await db.execute(select(Task).filter_by(project_id=project_id, title=title))
    membership = res.scalars().first()
    print(membership)
    if not membership:
        raise HTTPException(status_code=404, detail="Проект не найден")

    update_dict = task.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(membership, key, value)

    db.add(membership)
    await db.commit()
    await db.refresh(membership)

    return {"message": "Таска успешно обновлена", "title": title}
