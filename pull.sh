#!/usr/bin/env bash
set -e
docker login vm-registry.ipic.kz
docker pull vm-registry.ipic.kz/nlpmonitor:prod
docker pull vm-registry.ipic.kz/mariadb-columnstore:prod
