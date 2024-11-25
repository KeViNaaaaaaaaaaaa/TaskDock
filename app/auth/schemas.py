import re
import urllib.request
from typing import Self
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator, computed_field

from app.auth.utils import get_password_hash
from PIL import Image


class EmailModel(BaseModel):
    email: EmailStr = Field(description="Электронная почта")
    model_config = ConfigDict(from_attributes=True)


class NumModel(BaseModel):
    phone_number: str = Field(description="Номер телефона")
    model_config = ConfigDict(from_attributes=True)


class NickModel(BaseModel):
    nickname: str = Field(description="Ник")
    model_config = ConfigDict(from_attributes=True)


class UserBase(EmailModel):
    phone_number: str = Field(description="Номер телефона в международном формате, начинающийся с '+'")
    # photo_profile: str = 'https://i.pinimg.com/474x/13/31/a1/1331a1608c0d0c325e8968e19545a7db.jpg'
    nickname: str = Field(min_length=5, max_length=50, description="Ник, от 5 до 50 символов")
    first_name: str = Field(min_length=3, max_length=50, description="Имя, от 3 до 50 символов")
    last_name: str = Field(min_length=3, max_length=50, description="Фамилия, от 3 до 50 символов")

    @field_validator("phone_number")
    def validate_phone_number(cls, value: str) -> str:
        if not re.match(r'^\+\d{5,15}$', value):
            raise ValueError('Номер телефона должен начинаться с "+" и содержать от 5 до 15 цифр')
        return value

    # @field_validator("photo_profile")
    # def validate_url(cls, value: str) -> str:
    #     regex_pattern = re.compile(
    #         r"^(?:http|ftp)s?://"
    #         r"(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?$)"
    #         r"(?::\d+)?"
    #         r"(?:/?|[/?]\S+)$", re.IGNORECASE)
    #     if not re.match(regex_pattern, value):
    #         raise ValueError('Url ссылка на аватарку должна быть валидна')
    #     try:
    #         resource = urllib.request.urlopen(value)
    #         urllib.request.urlretrieve(value, "....jpg")
    #         return value
    #     except IOError:
    #         raise ValueError('Это должна быть картинка')


class SUserRegister(UserBase):
    password: str = Field(min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков")
    confirm_password: str = Field(min_length=5, max_length=50, description="Повторите пароль")

    @model_validator(mode="after")
    def check_password(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError("Пароли не совпадают")
        self.password = get_password_hash(self.password)  # хешируем пароль до сохранения в базе данных
        return self


class SUserAddDB(UserBase):
    password: str = Field(min_length=5, description="Пароль в формате HASH-строки")


class SUserAuth(EmailModel):
    password: str = Field(min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков")


class RoleModel(BaseModel):
    id: int = Field(description="Идентификатор роли")
    name: str = Field(description="Название роли")
    model_config = ConfigDict(from_attributes=True)


class SUserInfo(UserBase):
    id: int = Field(description="Идентификатор пользователя")
    role: RoleModel = Field(exclude=True)

    @computed_field
    def role_name(self) -> str:
        return self.role.name

    @computed_field
    def role_id(self) -> int:
        return self.role.id
