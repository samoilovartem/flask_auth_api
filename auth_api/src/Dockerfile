FROM python:3.11

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update --fix-missing

WORKDIR /app

ENV PYTHONPATH=${PYTHONPATH}:${PWD}

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt --no-cache-dir

COPY . /app/

CMD flask db upgrade && python manage.py runserver
