FROM python:3.12.8

ARG APP_ROOT=/var/www/django_frontend_demo
ENV PYTHONUNBUFFERED=1

RUN mkdir -p $APP_ROOT
WORKDIR $APP_ROOT

COPY . $APP_ROOT
RUN rm poetry.toml

RUN pip install pip
RUN pip install poetry lockfile && \
    poetry config virtualenvs.create false && \
    poetry config virtualenvs.in-project false && \
    poetry install --no-root
RUN apt update && \
  apt install -y \
  default-mysql-client \
  libxml2 \
  && apt-get clean && rm -rf /var/lib/apt/lists/*
