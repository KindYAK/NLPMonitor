#!/usr/bin/env bash
set -e
cd web
docker build . -f docker/Dockerfile -t vm-registry.ipic.kz/nlpmonitor:prod
docker login vm-registry.ipic.kz
docker push vm-registry.ipic.kz/nlpmonitor:prod

cd ..
cd mariadb-columnstore
docker build . -f Dockerfile -t vm-registry.ipic.kz/mariadb-columnstore:prod
docker login vm-registry.ipic.kz
docker push vm-registry.ipic.kz/mariadb-columnstore:prod
