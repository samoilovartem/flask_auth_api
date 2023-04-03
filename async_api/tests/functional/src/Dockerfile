FROM python:3.11

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update --fix-missing \
    && mkdir /tests && mkdir /tests/functional

WORKDIR /tests/functional

COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY . .

ENV PYTHONPATH "${PYTHONPATH}:/"
