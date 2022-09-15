FROM python:3.9.5-slim-buster

WORKDIR /api

#Do not buffer stdout and do not write bytecode to disk

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt /usr/api/requirements.txt
RUN pip install -r requirements.txt

#copy project:
COPY . /api/

