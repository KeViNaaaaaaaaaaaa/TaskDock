import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, delete, func, select

# Измененные импорты с учетом моделей и схем
from app import crud
from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.projects.models import Project, Task  # Импорты моделей
from app.models import Message
from app.projects.schemas import ProjectCreate, TaskCreate, ProjectPublic, TaskPublic, ProjectUpdate, TaskUpdate  # Импорты схем
from app.utils import send_email

router = APIRouter()



@router.get(
    "/projects",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=ProjectPublic,
)
def read_projects(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Получить список проектов
    """
    count_statement = select(func.count()).select_from(Project)
    count = session.exec(count_statement).one()

    statement = select(Project).offset(skip).limit(limit)
    projects = session.exec(statement).all()

    return ProjectPublic(data=projects, count=count)


@router.post(
    "/projects", dependencies=[Depends(get_current_active_superuser)], response_model=ProjectPublic
)
def create_project(session: SessionDep, project_in: ProjectCreate) -> Any:
    """
    Создать новый проект
    """
    project = crud.get_project_by_name(session=session, name=project_in.name)
    if project:
        raise HTTPException(
            status_code=400,
            detail="Проект с таким именем уже существует.",
        )

    project = crud.create_project(session=session, project_create=project_in)
    return project


@router.patch("/projects/{project_id}", response_model=ProjectPublic)
def update_project(
    *,
    session: SessionDep,
    project_id: uuid.UUID,
    project_in: ProjectUpdate,
) -> Any:
    """
    Обновить проект
    """
    db_project = session.get(Project, project_id)
    if not db_project:
        raise HTTPException(
            status_code=404,
            detail="Проект с таким id не найден.",
        )
    db_project = crud.update_project(session=session, db_project=db_project, project_in=project_in)
    return db_project


@router.delete("/projects/{project_id}", response_model=Message)
def delete_project(session: SessionDep, project_id: uuid.UUID) -> Any:
    """
    Удалить проект
    """
    db_project = session.get(Project, project_id)
    if not db_project:
        raise HTTPException(
            status_code=404,
            detail="Проект с таким id не найден.",
        )
    statement = delete(Task).where(col(Task.project_id) == project_id)
    session.exec(statement)  # type: ignore
    session.delete(db_project)
    session.commit()
    return Message(message="Проект удалён успешно")


@router.get("/tasks", response_model=TaskPublic)
def read_tasks(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Получить список задач
    """
    count_statement = select(func.count()).select_from(Task)
    count = session.exec(count_statement).one()

    statement = select(Task).offset(skip).limit(limit)
    tasks = session.exec(statement).all()

    return TaskPublic(data=tasks, count=count)


@router.post("/tasks", response_model=TaskPublic)
def create_task(session: SessionDep, task_in: TaskCreate) -> Any:
    """
    Создать новую задачу
    """
    task = crud.create_task(session=session, task_create=task_in)
    return task


@router.patch("/tasks/{task_id}", response_model=TaskPublic)
def update_task(
    *,
    session: SessionDep,
    task_id: uuid.UUID,
    task_in: TaskUpdate,
) -> Any:
    """
    Обновить задачу
    """
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(
            status_code=404,
            detail="Задача с таким id не найдена.",
        )
    db_task = crud.update_task(session=session, db_task=db_task, task_in=task_in)
    return db_task


@router.delete("/tasks/{task_id}", response_model=Message)
def delete_task(session: SessionDep, task_id: uuid.UUID) -> Any:
    """
    Удалить задачу
    """
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(
            status_code=404,
            detail="Задача с таким id не найдена.",
        )
    session.delete(db_task)
    session.commit()
    return Message(message="Задача удалена успешно")
