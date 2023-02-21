FROM python:3.10

RUN mkdir -p /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /app
RUN pip install -r /app/requirements.txt

WORKDIR /app

EXPOSE 8000
