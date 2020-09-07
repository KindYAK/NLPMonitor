FROM debian:10.4-slim

RUN apt-get update && \
    apt-get -f -y install locales wget && \
    sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN wget https://apertium.projectjj.com/apt/install-release.sh -O - | bash && \
    apt-get -f -y install apertium-all-dev
RUN git clone https://github.com/apertium/apertium-kaz.git && cd /apertium-kaz/ && ./autogen.sh && make install

RUN apt-get -f -y install python3-pip
RUN pip3 install Flask==1.1.2 waitress==1.4.4

COPY ./apertium-kaz/ /apertium-kaz/
COPY ./kaz-tagger/ /kaz-tagger/

WORKDIR /apertium-kaz/
CMD python3 waitress_serve.py
