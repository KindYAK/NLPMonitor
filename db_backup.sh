#!/bin/bash -e
cd /var/www/nlpmonitor
/usr/local/bin/docker-compose exec -T db chmod 777 /bin/db_backup.sh
/usr/local/bin/docker-compose exec -T db /bin/db_backup.sh
