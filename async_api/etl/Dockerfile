FROM python:3.11

RUN apt-get update --fix-missing

WORKDIR /app/

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt --no-cache-dir

COPY . /app/

CMD ["python", "main.py"]
