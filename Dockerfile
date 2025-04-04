FROM python:3.12-slim

WORKDIR /app

RUN apt-get update

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

COPY . .

EXPOSE 8000

CMD ["poetry", "run", "python", "source/manage.py", "runserver", "0.0.0.0:8000"]
