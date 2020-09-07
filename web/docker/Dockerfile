FROM python:3.7.7

RUN apt-get update && apt-get install -y gettext
RUN apt-get install -y --fix-missing texlive-latex-extra
RUN apt-get -y --fix-missing install biber texlive-lang-cyrillic \
             fonts-cmu texlive-xetex texlive-fonts-extra \
             font-manager cm-super

COPY ./requirements-base.txt /tmp/requirements-base.txt
RUN pip3 install -r /tmp/requirements-base.txt

COPY ./requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

COPY ./docker/bin /app/bin
ENV PATH=$PATH:/app/bin
RUN chmod +x /app/bin/*

COPY . /opt/app

WORKDIR "/opt/app"
