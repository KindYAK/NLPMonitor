FROM centos:7

COPY yum_repos /etc/yum.repos.d/

# additional dependencies for docker image
RUN export USER=root && \
    /bin/echo "export USER=root" >> /root/.bashrc && \
    groupadd -r mysql && \
    useradd -r -g mysql mysql && \
    yum -y install epel-release && \
    yum -y install expect zlib rsyslog libaio boost file sudo libnl net-tools sysvinit-tools runit which psmisc lsof snappy rsync pwgen bind-utils openssh-server openssh-clients && \
    yum -y install mariadb-columnstore-client mariadb-columnstore-common mariadb-columnstore-libs mariadb-columnstore-platform mariadb-columnstore-server mariadb-columnstore-shared mariadb-columnstore-storage-engine && \
    sudo yum install -y libuv libxml2  && \
    yum clean all && \
    rm -rf /var/cache/yum && \
    /usr/bin/systemd-machine-id-setup && \
    ln -s /usr/local/mariadb/columnstore/lib/libcalmysql.so.1.0.0 /usr/local/mariadb/columnstore/mysql/lib/plugin/libcalmysql.so && \
    ln -s /usr/local/mariadb/columnstore/lib/libudf_mysql.so.1.0.0 /usr/local/mariadb/columnstore/mysql/lib/plugin/libudf_mysql.so && \
    ln -s /usr/local/mariadb/columnstore/lib/is_columnstore_tables.so.1.0.0 /usr/local/mariadb/columnstore/mysql/lib/plugin/is_columnstore_tables.so && \
    ln -s /usr/local/mariadb/columnstore/lib/is_columnstore_columns.so.1.0.0 /usr/local/mariadb/columnstore/mysql/lib/plugin/is_columnstore_columns.so && \
    ln -s /usr/local/mariadb/columnstore/lib/is_columnstore_extents.so.1.0.0 /usr/local/mariadb/columnstore/mysql/lib/plugin/is_columnstore_extents.so && \
    ln -s /usr/local/mariadb/columnstore/lib/is_columnstore_files.so.1.0.0 /usr/local/mariadb/columnstore/mysql/lib/plugin/is_columnstore_files.so && \
    chown -R mysql:mysql /usr/local/mariadb/columnstore/mysql

RUN yum --enablerepo=mariadb-columnstore clean metadata && \
yum groups mark remove "MariaDB ColumnStore" && \
yum -y groupinstall "MariaDB ColumnStore" && \
yum --enablerepo=mariadb-columnstore-tools clean metadata && \
yum -y install mariadb-columnstore-tools

COPY ssh_config /etc/ssh/
COPY ssh_keys /root/.ssh
RUN chmod 400 /etc/ssh/* && \
    chmod 700 /root/.ssh && \
    chmod 640 /root/.ssh/authorized_keys && \
    chmod 640 /root/.ssh/known_hosts && \
    chmod 600 /root/.ssh/id_rsa && \
    chmod 644 /root/.ssh/id_rsa.pub

COPY service /etc/service/
COPY dbinit runit_bootstrap wait_for_columnstore_active /usr/sbin/
COPY init.d-rsyslog /etc/init.d/rsyslog
COPY mysql /usr/bin

RUN chmod 755 /etc/service/*/run /etc/service/*/finish /usr/sbin/runit_bootstrap /usr/sbin/dbinit /usr/sbin/wait_for_columnstore_active /etc/init.d/rsyslog /usr/bin/mysql && \
    mkdir -p /var/log/mariadb/columnstore && \
    mkdir /docker-entrypoint-initdb.d && \
    mkdir /log

# default postConfigure input to create single node cluster
ENV MARIADB_CS_POSTCFG_INPUT="1\ncolumnstore-1\n1\n1\n" \
MARIADB_CS_NUM_BLOCKS_PCT=1024M \
MARIADB_CS_TOTAL_UM_MEMORY=256M

EXPOSE 3306
EXPOSE 22

VOLUME /usr/local/mariadb/columnstore/etc
VOLUME /usr/local/mariadb/columnstore/data1
VOLUME /usr/local/mariadb/columnstore/local
VOLUME /usr/local/mariadb/columnstore/mysql/db
VOLUME /backup

COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod 755 /usr/local/bin/docker-entrypoint.sh && \
    ln -s /usr/local/bin/docker-entrypoint.sh /docker-entrypoint.sh # backwards compat
ENTRYPOINT ["docker-entrypoint.sh"]

# Custom configuration
COPY my.cnf /usr/local/mariadb/columnstore/mysql/

CMD ["/usr/sbin/runit_bootstrap"]
