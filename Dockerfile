FROM jfloff/alpine-python:3.6-onbuild

WORKDIR /app

RUN pip install flask redis requests

COPY . /app

CMD python server.py