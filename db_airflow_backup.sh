#!/bin/bash -e
cd /var/www/nlpmonitor
/usr/local/bin/docker-compose exec -T airflow-postgresql chmod 777 /bin/db_backup.sh
/usr/local/bin/docker-compose exec -T airflow-postgresql /bin/db_backup.sh
