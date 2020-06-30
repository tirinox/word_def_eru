FROM python:3-alpine

WORKDIR /app

RUN apk add  --update --no-cache build-base py3-configobj py3-pip py3-setuptools python3 python3-dev  \
                       # Pillow dependencies
                       jpeg-dev \
                       zlib-dev \
                       libwebp-dev \
                       freetype-dev \
                       lcms2-dev \
                       openjpeg-dev \
                       tiff-dev \
                       tk-dev \
                       tcl-dev \
                       harfbuzz-dev \
                       fribidi-dev

#ENV LIBRARY_PATH=/lib:/usr/lib

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD python server.py