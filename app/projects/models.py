from datetime import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.auth.models import User
from app.dao.database import Base
from typing import Optional, List
import enum


class ProjectRole(str, enum.Enum):
    CREATOR = "Creator"
    MEMBER = "Member"


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


class ProjectMembership(Base):
    __tablename__ = 'project_memberships'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey('projects.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    role: Mapped[ProjectRole] = mapped_column(Enum(ProjectRole), nullable=False)

    project: Mapped["Project"] = relationship("Project", back_populates="members")

    def __repr__(self):
        return f"ProjectMembership(id={self.id}, user_id={self.user_id}, role={self.role})"


class TaskStatus(str, enum.Enum):
    Grooming = "Grooming"
    InProgress = "In Progress"
    Dev = "Dev"
    Done = "Done"


# class RoleMembers(str, enum.Enum):
#     User = {'1': 'User'}
#     SuperAdmin = {'4': 'SuperAdmin'}


class TaskPriority(str, enum.Enum):
    Low = "Low"
    Medium = "Medium"
    High = "High"


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
    # due_date: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    tester_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('users.id'), nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="tasks")

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"
