FROM python:3.11

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update --fix-missing

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt --no-cache-dir

COPY . /app/

CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker"]
