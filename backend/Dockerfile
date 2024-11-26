# Базовый образ Python
FROM python:3.10

# Устанавливаем переменную среды для немедленной записи вывода
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию
WORKDIR /app/

# Устанавливаем uv
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:0.4.15 /uv /bin/uv

# Добавляем директорию виртуального окружения в PATH
ENV PATH="/app/.venv/bin:$PATH"

# Кэширование для uv
ENV UV_LINK_MODE=copy

# Устанавливаем зависимости из requirements.txt
COPY ./requirements.txt /app/
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Копируем проект в контейнер
COPY ./scripts /app/scripts
COPY ./app /app/app

# Запуск FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]