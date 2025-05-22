FROM python:3.12 as builder
WORKDIR /app
RUN pip install poetry==1.8.3
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false
RUN poetry install
COPY ./app ./app
COPY settings.toml settings.toml
COPY main.py main.py
CMD ["python", "main.py"]