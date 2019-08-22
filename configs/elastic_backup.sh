#!/bin/bash
SNAPSHOT=`date +%Y%m%d-%H%M%S`
curl -XPUT "localhost:9200/_snapshot/my_backup/$SNAPSHOT?wait_for_completion=true"
find /backup/ -type f -mtime +60 -name '*' -delete
