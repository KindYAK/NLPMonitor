FROM python:3.7.3

COPY ./docker/bin /app/bin
ENV PATH=$PATH:/app/bin
RUN chmod +x /app/bin/*

COPY ./requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

RUN apt-get update && apt-get install -y gettext

COPY . /opt/app

WORKDIR "/opt/app"
