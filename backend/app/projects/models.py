from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base
from app.models import User
from typing import Optional, List
import enum


# Роли в проекте
class ProjectRole(str, enum.Enum):
    CREATOR = "Creator"
    MEMBER = "Member"


# Модель для проекта
class Project(Base):
    __tablename__ = 'projects'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status: Mapped[str] = mapped_column(String, default="Active", server_default="Active")

    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="project")
    members: Mapped[List["ProjectMembership"]] = relationship("ProjectMembership", back_populates="project")

    def __repr__(self):
        return f"Project(id={self.id}, title={self.title})"


# Модель для участия в проекте (пользователи в проектах)
class ProjectMembership(Base):
    __tablename__ = 'project_memberships'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey('projects.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    role: Mapped[ProjectRole] = mapped_column(Enum(ProjectRole), nullable=False)

    project: Mapped["Project"] = relationship("Project", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="memberships")

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
class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey('projects.id'), nullable=False)
    assignee_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('project_memberships.user_id'), nullable=True)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.Grooming)
    priority: Mapped[TaskPriority] = mapped_column(Enum(TaskPriority), default=TaskPriority.Medium)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tester_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('users.id'), nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="tasks")
    assignee: Mapped["ProjectMembership"] = relationship("ProjectMembership", back_populates="tasks", foreign_keys=[assignee_id])

    def __repr__(self):
        return f"Task(id={self.id}, title={self.title}, status={self.status})"

