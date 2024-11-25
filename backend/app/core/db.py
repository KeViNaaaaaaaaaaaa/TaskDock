from sqlmodel import Session, create_engine, select

from app import crud
from datetime import datetime
from typing import Dict, Any
from app.core.config import settings
from sqlalchemy import Integer, TIMESTAMP, func
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker, AsyncSession
from app.models import User, UserCreate
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, declared_attr
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI), echo=True)

# Асинхронная сессия
AsyncSessionMaker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Асинхронная база
Base = declarative_base()

# Инициализация базы данных: создание таблиц
async def init_db():
    async with engine.begin() as conn:
        # Создание всех таблиц
        await conn.run_sync(Base.metadata.create_all)

    # Инициализация пользователя
    async with AsyncSessionMaker() as session:
        async with session.begin():
            user = await session.execute(
                select(User).where(User.email == settings.FIRST_SUPERUSER)
            )
            user = user.scalars().first()
            if not user:
                user_in = UserCreate(
                    email=settings.FIRST_SUPERUSER,
                    password=settings.FIRST_SUPERUSER_PASSWORD,
                    is_superuser=True,
                )
                await crud.create_user(session=session, user_create=user_in)

class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует объект модели в словарь."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self) -> str:
        """Строковое представление объекта для удобства отладки."""
        return f"<{self.__class__.__name__}(id={self.id}, created_at={self.created_at}, updated_at={self.updated_at})>"

# Инициализация базы данных: создание таблиц, если они не существуют
