FROM python:3.7.4

RUN apt-get update
RUN apt-get install -y python3-setuptools build-essential postgresql-server-dev-all libpq-dev gcc libboost-all-dev wget git cmake

ENV ARTM_SHARED_LIBRARY=/bigartm/libartm.so

COPY bigartm /bigartm/
RUN pip install /bigartm/bigartm-0.10.0-cp37-cp37m-linux_x86_64.whl
RUN git clone https://github.com/bigartm/visartm.git

COPY numpy-1.17.2-cp37-cp37m-manylinux1_x86_64.whl /numpy-1.17.2-cp37-cp37m-manylinux1_x86_64.whl
RUN pip install /numpy-1.17.2-cp37-cp37m-manylinux1_x86_64.whl
COPY requirements.txt /visartm/requirements.txt
RUN pip install -r /visartm/requirements.txt
RUN pip install scipy
RUN pip install scikit-learn

WORKDIR /visartm/
COPY django_settings/ /visartm/visartm/

CMD python manage.py makemigrations && python manage.py migrate && gunicorn visartm.wsgi -b 0.0.0.0:8000 --timeout=30 --workers=4
