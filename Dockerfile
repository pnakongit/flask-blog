FROM python:3.11-slim

LABEL maintainer="p.nakonechnyi@gmail.com"

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=src/blog.py

WORKDIR app/

RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src
COPY ./boot.sh ./boot.sh

RUN mkdir ./data

RUN adduser \
    --disabled-password \
    --no-create-home \
    blog_user

RUN chown -R blog_user ./data && chmod -R 755 ./data
RUN chown -R blog_user ./src/app/translations && chmod -R 755 ./src/app/translations

USER blog_user
