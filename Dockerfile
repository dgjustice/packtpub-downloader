FROM python:3.7-slim-buster

ADD . /app
WORKDIR /app

RUN apt-get update && \
	apt-get install -y git build-essential && \
	apt-get autoclean && \
	pip install --upgrade pip setuptools && \
	pip install poetry==1.0.0 && \
	poetry config virtualenvs.create false && \
	poetry install

CMD "python -m packt_downloader"
