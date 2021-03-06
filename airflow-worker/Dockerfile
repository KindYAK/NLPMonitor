FROM bitnami/minideb-extras:stretch-r484
LABEL maintainer "Bitnami <containers@bitnami.com>"

ENV BITNAMI_PKG_CHMOD="-R g+rwX" \
    BITNAMI_PKG_EXTRA_DIRS="/opt/bitnami/airflow/dags" \
    HOME="/"

# Install required system packages and dependencies
RUN install_packages libbsd0 libbz2-1.0 libc6 libcomerr2 libedit2 libffi6 libgcc1 libgssapi-krb5-2 libicu57 libk5crypto3 libkeyutils1 libkrb5-3 libkrb5support0 liblzma5 libmariadbclient18 libncurses5 libnss-wrapper libreadline7 libsasl2-2 libsqlite3-0 libssl1.1 libstdc++6 libtinfo5 libuuid1 libxml2 libxslt1.1 zlib1g
RUN bitnami-pkg install python-3.6.9-1 --checksum 16bf895318d5581937b3b5e73b55d7c7180a8ef42af8d0a8d4dd010bd0a0408d
RUN bitnami-pkg install postgresql-client-10.10.0-1 --checksum 77f89198ede517c8355f466642643cc787989b16bd136c0efcfea0a2d21282cb
RUN bitnami-pkg unpack airflow-worker-1.10.5-1 --checksum 078ee3a40c6e2d42bcef0c75eee66acb26902be3651aa2d05009452c82b3859a
RUN install_packages python3-dev python3-setuptools build-essential postgresql-server-dev-all libpq-dev gcc libboost-all-dev

COPY rootfs /
ENV AIRFLOW_DATABASE_HOST="postgresql" \
    AIRFLOW_DATABASE_NAME="bitnami_airflow" \
    AIRFLOW_DATABASE_PASSWORD="bitnami1" \
    AIRFLOW_DATABASE_PORT_NUMBER="5432" \
    AIRFLOW_DATABASE_USERNAME="bn_airflow" \
    AIRFLOW_DATABASE_USE_SSL="no" \
    AIRFLOW_EXECUTOR="SequentialExecutor" \
    AIRFLOW_FERNET_KEY="" \
    AIRFLOW_HOME="/opt/bitnami/airflow" \
    AIRFLOW_HOSTNAME_CALLABLE="" \
    AIRFLOW_REDIS_USE_SSL="no" \
    AIRFLOW_WEBSERVER_HOST="airflow" \
    AIRFLOW_WEBSERVER_PORT_NUMBER="8080" \
    AIRFLOW_WORKER_PORT_NUMBER="8793" \
    BITNAMI_APP_NAME="airflow-worker" \
    BITNAMI_IMAGE_VERSION="1.10.5-debian-9-r20" \
    C_FORCE_ROOT="True" \
    LD_LIBRARY_PATH="/opt/bitnami/python/lib/:/opt/bitnami/airflow/venv/lib/python3.6/site-packages/numpy/.libs/:$LD_LIBRARY_PATH" \
    LD_PRELOAD="/usr/lib/libnss_wrapper.so" \
    LNAME="airflow" \
    NAMI_PREFIX="/.nami" \
    NSS_WRAPPER_GROUP="/opt/bitnami/airflow/nss_group" \
    NSS_WRAPPER_PASSWD="/opt/bitnami/airflow/nss_passwd" \
    PATH="/opt/bitnami/python/bin:/opt/bitnami/postgresql/bin:/opt/bitnami/airflow-worker/bin:/opt/bitnami/airflow/venv/bin:$PATH" \
    REDIS_HOST="redis" \
    REDIS_PASSWORD="" \
    REDIS_PORT_NUMBER="6379" \
    REDIS_USER="" \
    ARTM_SHARED_LIBRARY=/bigartm/libartm.so

RUN pip install --upgrade pip
RUN pip install --upgrade --ignore-installed setuptools

COPY requirements-base.txt /requirements-base.txt
RUN pip install -r /requirements-base.txt

RUN pip install --ignore-installed tensorflow>=1.11.0
RUN python -m textblob.download_corpora
RUN python -m nltk.downloader stopwords
RUN mkdir /.local && chmod 775 /.local

COPY bigartm /bigartm/
RUN pip install /bigartm/bigartm-0.10.0-cp36-cp36m-linux_x86_64.whl

COPY requirements.txt /requirements.txt
RUN pip install --ignore-installed -r /requirements.txt

EXPOSE 8793

WORKDIR /opt/bitnami/airflow/dags/
USER 1001
ENTRYPOINT [ "/app-entrypoint.sh" ]
CMD [ "/run.sh" ]
