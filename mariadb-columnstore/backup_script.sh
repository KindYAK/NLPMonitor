# Backup

docker-compose exec db mcsadmin shutdownSystem y
docker-compose exec db /usr/local/mariadb/columnstore/tools/backuprestore/columnstoreBackup -zv 0.0.0.0 /backup/
docker-compose exec db mcsadmin startSystem y

# Restore - on clear volumes!!! with no mysqld and columnstore services
#docker-compose exec db /usr/sbin/sshd
#docker-compose exec db mcsadmin shutdownSystem y
#docker-compose exec db rm -rf /usr/local/mariadb/columnstore/data*/000.dir
#docker-compose exec db rm -rf /usr/local/mariadb/columnstore/data1/systemFiles/dbrm/*
#docker-compose exec db rm -rf /usr/local/mariadb/columnstore/mysql/db/nlpmonitor
#docker-compose exec db rm -rf /usr/local/mariadb/columnstore/mysql/db/columnstore_info
#docker-compose exec db /usr/local/mariadb/columnstore/bin/clearShm
#docker-compose exec db /usr/local/mariadb/columnstore/tools/backuprestore/columnstoreRestore -zv /backup/ 0.0.0.0

#Then just restart with enabled mysqld service or attempt to:
#docker-compose exec db /usr/local/mariadb/columnstore/mysql/bin/mysqld --user=root &
#docker-compose exec db mcsadmin startSystem y
