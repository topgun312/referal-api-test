FROM python:3.10

RUN mkdir /fastapi_app

WORKDIR /fastapi_app

RUN pip install poetry

COPY pyproject.toml poetry.lock .

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

COPY . .

ENV PYTHONPATH=/fastapi_app

RUN chmod a+x docker/*.sh