#!/bin/bash
pg_dump --host=localhost --port=5432 --username=$POSTGRES_USER --format=t --file=/backup/backup`date +%F-%H%M`.dump $POSTGRES_DB
find /backup/ -type f -mtime +30 -name '*.dump' -delete
