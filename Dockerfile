FROM python:3.7-slim-buster

ADD . /app
WORKDIR /app

RUN apt-get update && apt-get install -y build-essential curl git && apt-get autoclean && pip install --upgrade pip setuptools 

RUN  pip install poetry==1.0.0 && poetry config virtualenvs.create false

ADD poetry.lock /tmp
ADD pyproject.toml /tmp
RUN cd /tmp && poetry install

CMD "python main.py"
