import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router  # Официальный роутер
from app.projects.router import router as router_projects

from app.core.config import settings
from app.core.db import init_db


def custom_generate_unique_id(route):
    tag = route.tags[0] if route.tags else "default"
    return f"{tag}-{route.name}"


# Настраиваем Sentry
if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

# Создаём приложение
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.all_cors_origins or ["*"],  # Разрешаем все источники, если не указано
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение статики
# app.mount("/static", StaticFiles(directory="app/static"), name="static")


# Событие старта приложения
@app.on_event("startup")
async def on_startup():
    await init_db()


# Домашний роут
@app.get("/", tags=["home"])
def home_page():
    return {
        "message": "Добро пожаловать!"
    }


# Подключение роутеров
app.include_router(api_router, prefix=settings.API_V1_STR)  # Официальный роутер
app.include_router(router_projects)  # Проекты
