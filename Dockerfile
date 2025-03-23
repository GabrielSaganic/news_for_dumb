FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y locales && \
    sed -i '/hr_HR.UTF-8/s/^# //g' /etc/locale.gen && \
    sed -i '/sr_RS.UTF-8/s/^# //g' /etc/locale.gen && \
    sed -i '/bs_BA.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen

ENV LANG hr_HR.UTF-8
ENV LANGUAGE hr_HR:hr
ENV LC_ALL hr_HR.UTF-8

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

COPY . .

EXPOSE 8000

CMD ["poetry", "run", "python", "source/manage.py", "runserver", "0.0.0.0:8000"]
