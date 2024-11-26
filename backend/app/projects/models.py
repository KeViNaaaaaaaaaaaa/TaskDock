from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Enum as SQLAEnum
from typing import Optional, List
import enum


# Роли в проекте
class ProjectRole(str, enum.Enum):
    CREATOR = "Creator"
    MEMBER = "Member"


# Модель для проекта
class Project(SQLModel, table=True):
    __tablename__ = 'projects'

    id: int = Field(default=None, primary_key=True, index=True)
    title: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(
        default="Active",
        sa_column_kwargs={"server_default": "Active"}
    )

    # Отношения
    tasks: List["Task"] = Relationship(back_populates="project")
    members: List["ProjectMembership"] = Relationship(back_populates="project")

    def __repr__(self):
        return f"Project(id={self.id}, title={self.title})"


# Модель для участия в проекте (пользователи в проектах)
class ProjectMembership(SQLModel, table=True):
    __tablename__ = 'project_memberships'

    id: int = Field(default=None, primary_key=True, index=True)
    project_id: int = Field(nullable=False, foreign_key="projects.id")
    user_id: int = Field(nullable=False, foreign_key="users.id")
    role: ProjectRole = Field(sa_column=SQLAEnum(ProjectRole))

    # Отношения
    project: "Project" = Relationship(back_populates="members")
    user: "User" = Relationship(back_populates="memberships")

    def __repr__(self):
        return f"ProjectMembership(id={self.id}, user_id={self.user_id}, role={self.role})"


# Статус задачи
class TaskStatus(str, enum.Enum):
    Grooming = "Grooming"
    InProgress = "In Progress"
    Dev = "Dev"
    Done = "Done"


# Приоритет задачи
class TaskPriority(str, enum.Enum):
    Low = "Low"
    Medium = "Medium"
    High = "High"


# Модель задачи
class Task(SQLModel, table=True):
    __tablename__ = 'tasks'

    id: int = Field(default=None, primary_key=True, index=True)
    title: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    project_id: int = Field(nullable=False, foreign_key="projects.id")
    assignee_id: Optional[int] = Field(default=None, foreign_key="project_memberships.user_id")
    status: TaskStatus = Field(sa_column=SQLAEnum(TaskStatus), default=TaskStatus.Grooming)
    priority: TaskPriority = Field(sa_column=SQLAEnum(TaskPriority), default=TaskPriority.Medium)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    tester_id: Optional[int] = Field(default=None, foreign_key="users.id")

    # Отношения
    project: "Project" = Relationship(back_populates="tasks")
    assignee: Optional["ProjectMembership"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Task.assignee_id]"}
    )

    def __repr__(self):
        return f"Task(id={self.id}, title={self.title}, status={self.status})"
