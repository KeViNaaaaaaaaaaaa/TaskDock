from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


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


class ProjectDelete(BaseModel):
    id: int
    title: str
    pass


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(ProjectBase):
    status: Optional[str]


class ProjectPublic(ProjectBase):
    id: int
    owner: str
    created_at: datetime
    updated_at: Optional[datetime]
    status: str
    members: List[str]
    tasks: List[str]

    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    tester_id: int
    # due_data: (datetime.now() + timedelta(10)).strftime("%d/%m/%y %I:%M")

    class Config:
        arbitrary_types_allowed = False


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    status: Optional[str]
    priority: Optional[str]
    assignee_id: Optional[int]  # id исполнителя
    tester_id: Optional[int]  # id ответственного за тестировку


class TaskPublic(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
    project_id: int
    assignee_id: Optional[int]  # Исполнитель
    tester_id: Optional[int]  # Ответственный за тестирование

    class Config:
        from_attributes = True
