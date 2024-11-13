from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List


# Модель пользователя (с минимальными данными)
class UserBase(BaseModel):
    nickname: str
    first_name: str
    last_name: str


class ProjectMembershipBase(BaseModel):
    nickname: str
    first_name: str
    last_name: str


class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(ProjectBase):
    status: Optional[str]


class ProjectRead(ProjectBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    status: str
    members: List[ProjectMembershipBase]  # Список участников с минимальными данными

    class Config:
        orm_mode = True

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    status: Optional[str]
    priority: Optional[str]
    assignee_id: Optional[int]  # id исполнителя
    tester_id: Optional[int]  # id ответственного за тестировку


class TaskRead(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
    project_id: int
    assignee_id: Optional[int]  # Исполнитель
    tester_id: Optional[int]  # Ответственный за тестирование

    class Config:
        orm_mode = True
