from fastapi import FastAPI, Query
from utils import json_to_dict_list
import os
from enum import Enum
from pydantic import BaseModel, EmailStr, Field, field_validator, ValidationError
from datetime import date, datetime
from typing import Optional
import re

path_to_json = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'students.json')

app = FastAPI()

class UserRegistration(BaseModel):
    username: str
    password: str
    email: str

class Major(str, Enum):
    informatics = "Информатика"
    economics = "Экономика"
    law = "Право"
    medicine = "Медицина"
    engineering = "Инженерия"
    languages = "Языки"

class Student(BaseModel):
    student_id: int
    phone_number: str = Field(default=..., description="Номер телефона в международном формате, начинающийся с '+'")
    first_name: str = Field(default=..., min_length=1, max_length=50, description="Имя студента, от 1 до 50 символов")
    last_name: str = Field(default=..., min_length=1, max_length=50, description="Фамилия студента, от 1 до 50 символов")
    date_of_birth: date = Field(default=..., description="Дата рождения студента в формате ГГГГ-ММ-ДД")
    email: EmailStr = Field(default=..., description="Электронная почта студента")
    address: str = Field(default=..., min_length=10, max_length=200, description="Адрес студента, не более 200 символов")
    enrollment_year: int = Field(default=..., ge=2002, description="Год поступления должен быть не меньше 2002")
    major: Major = Field(default=..., description="Специальность студента")
    course: int = Field(default=..., ge=1, le=5, description="Курс должен быть в диапазоне от 1 до 5")
    special_notes: Optional[str] = Field(default=None, max_length=500,
                                         description="Дополнительные заметки, не более 500 символов")

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, values: str) -> str:
        if not re.match(r'^\+\d{1,15}$', values):
            raise ValueError('Номер телефона должен начинаться с "+" и содержать от 1 до 15 цифр')
        return values

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, values: date):
        if values and values >= datetime.now().date():
            raise ValueError('Дата рождения должна быть в прошлом')
        return values


@app.get("/students")
def get_all_students():
    return json_to_dict_list(path_to_json)


@app.get("/")
def home_page():
    return {"message": "Привет, Хабр!"}


@app.get("/students/{role}")
def get_students_with_projects(
        role: str,
        active_project: Optional[bool] = Query(None),
        archived_project: Optional[bool] = Query(None)
):
    filtered_students = []
    students = json_to_dict_list(path_to_json)

    for student in students:
        if student["role"] == role:

            act = True
            arc = True

            has_active_project = any(
                project["status"] == "Active" for project in student["current_projects"]
            ) if active_project is not None else True

            if active_project is not None and has_active_project != active_project:
                act = False

            has_archived_project = any(
                project["status"] == "Archived" for project in student["history_projects"]
            ) if archived_project is not None else True

            if archived_project is not None and has_archived_project != archived_project:
                arc = False

            if act and arc:
                filtered_students.append(student)

    return filtered_students

@app.post("/register/")
async def register_user(user: UserRegistration):
    # Логика регистрации пользователя
    return {"message": "User registered successfully", "user": user}