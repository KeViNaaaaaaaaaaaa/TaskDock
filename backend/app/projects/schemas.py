from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


# Enum для статуса задачи
class TaskStatus(str, Enum):
    grooming = "Grooming"
    in_progress = "In Progress"
    dev = "Dev"
    done = "Done"


# Enum для приоритета задачи
class TaskPriority(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"


class UserBase(BaseModel):
    nickname: str
    first_name: str
    last_name: str


class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None


# Модель для удаления проекта
class ProjectDelete(BaseModel):
    id: int
    title: str


# Модель для создания проекта
class ProjectCreate(ProjectBase):
    pass


# Модель для обновления проекта
class ProjectUpdate(ProjectBase):
    status: Optional[str] = None


# Модель для публичного представления проекта
class ProjectPublic(ProjectBase):
    id: int
    owner: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    status: str
    members: List[str]
    tasks: List[str]

    class Config:
        orm_mode = True  # Использование orm_mode для работы с SQLAlchemy моделями


# Модель для задачи
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus
    priority: TaskPriority
    tester_id: int

    class Config:
        arbitrary_types_allowed = False


# Модель для создания задачи
class TaskCreate(TaskBase):
    pass


# Модель для обновления задачи
class TaskUpdate(TaskBase):
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee_id: Optional[int] = None  # id исполнителя
    tester_id: Optional[int] = None  # id ответственного за тестирование


# Модель для публичного представления задачи
class TaskPublic(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
    project_id: int
    assignee_id: Optional[int]  # Исполнитель
    tester_id: Optional[int]  # Ответственный за тестирование

    class Config:
        orm_mode = True  # Использование orm_mode для работы с SQLAlchemy моделями
