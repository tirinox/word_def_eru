FROM jfloff/alpine-python:3.7-onbuild

RUN apk add build-base python-dev py-pip jpeg-dev zlib-dev
ENV LIBRARY_PATH=/lib:/usr/lib

WORKDIR /app

RUN pip install flask redis requests Pillow

COPY . /app

CMD python server.py