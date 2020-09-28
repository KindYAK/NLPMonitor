#!/bin/bash
curl -X PUT "localhost:9200/_snapshot/my_backup?pretty" -H 'Content-Type: application/json' -d'
{
  "type": "fs",
  "settings": {
    "location": "/backup/"
  }
}
'

curl -X PUT "localhost:9200/_snapshot/my_backup/snapshot_1?wait_for_completion=true&pretty"

find /backup/ -type f -mtime +30 -name '*.dump' -delete
