# from fastapi import Query
# from utils import json_to_dict_list
# import os
# from enum import Enum
# from pydantic import BaseModel, EmailStr, Field
# from typing import Optional, List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth.router import router as router_auth
from app.projects.router import router as router_projects

from fastapi.staticfiles import StaticFiles
from app.dao.database import init_db

app = FastAPI()

# Добавляем middleware для CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем все источники
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все методы
    allow_headers=["*"],  # Разрешаем все заголовки
)

app.mount('/static', StaticFiles(directory='app/static'), name='static')

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.get("/")
def home_page():
    return {
        "message": "Добро пожаловать! Пусть эта заготовка станет удобным инструментом для вашей работы и "
                   "приносит вам пользу!"
    }


# path_to_json = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'students.json')


# class UserRegistration(BaseModel):
#     username: str
#     password: str
#     email: str
#
#
# class Role(str, Enum):
#     admin = "admin"
#     manager = "manager"
#     user = "user"
#
#
# class RoleProj(str, Enum):
#     developer = "developer"
#     manager = "manager"
#     tester = "tester"
#
#
# class Stat(str, Enum):
#     active = "Active"
#     archived = "Archived"
#
#
# class Project(BaseModel):
#     project_id: int = Field(..., description="Идентификатор проекта")
#     role: RoleProj = Field(..., description="Роль студента в проекте")
#     status: Stat = Field(..., description="Статус проекта, например, Active или Archived")
#
#
# class SStudent(BaseModel):
#     id: int
#     first_name: str = Field(..., min_length=1, max_length=50, description="Имя студента")
#     last_name: str = Field(..., min_length=1, max_length=50, description="Фамилия студента")
#     email: EmailStr = Field(..., description="Электронная почта студента")
#     role: Role = Field(..., description="Роль пользователя, например, admin или user")
#     avatar_url: str = Field(..., description="URL к аватару студента")
#     current_projects: List[Project] = Field(default=[], description="Список текущих проектов студента")
#     history_projects: List[Project] = Field(default=[], description="Список завершенных проектов студента")
#     special_notes: Optional[str] = Field(None, max_length=500, description="Дополнительные заметки")
#
#
# @app.get("/student", response_model=SStudent)
# def get_student_from_param_id(id: int):
#     students = json_to_dict_list(path_to_json)
#     for student in students:
#         if student["id"] == id:
#             return student
#
#
# @app.get("/students", response_model=SStudent)
# def get_all_students():
#     return json_to_dict_list(path_to_json)
#
#
# class RBStudent:
#     def __init__(self, role: str, active_project: Optional[bool] = Query(None),
#                  archived_project: Optional[bool] = Query(None)):
#         self.role: str = role
#         self.active_project: Optional[bool] = active_project
#         self.archived_project: Optional[bool] = archived_project
#
#
# @app.get("/students/{role}")
# def get_students_with_projects(request_body: RBStudent) -> List[SStudent]:
#     filtered_students = []
#     students = json_to_dict_list(path_to_json)
#
#     for student in students:
#         if student["role"] == request_body.role:
#
#             act = True
#             arc = True
#
#             has_active_project = any(
#                 project["status"] == "Active" for project in student["current_projects"]
#             ) if request_body.active_project is not None else True
#
#             if request_body.active_project is not None and has_active_project != request_body.active_project:
#                 act = False
#
#             has_archived_project = any(
#                 project["status"] == "Archived" for project in student["history_projects"]
#             ) if request_body.archived_project is not None else True
#
#             if request_body.archived_project is not None and has_archived_project != request_body.archived_project:
#                 arc = False
#
#             if act and arc:
#                 filtered_students.append(student)
#
#     return filtered_students
#
#
# @app.post("/add_student")
# def add_student_handler(student: SStudent):
#     student_dict = student.dict()
#     check = add_student(student_dict)
#     if check:
#         return {"message": "Студент успешно добавлен!"}
#     else:
#         return {"message": "Ошибка при добавлении студента"}
#
#
# @app.post("/register/")
# async def register_user(user: UserRegistration):
#     return {"message": "User registered successfully", "user": user}


app.include_router(router_auth)
app.include_router(router_projects)
