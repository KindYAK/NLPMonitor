#!/usr/bin/env bash
set -e
cd web
docker build . -f docker/Dockerfile -t vm-registry.ipic.kz/nlpmonitor:prod
docker login vm-registry.ipic.kz
docker push vm-registry.ipic.kz/nlpmonitor:prod

cd ..
cd airflow-worker
docker build . -f Dockerfile -t vm-registry.ipic.kz/airflow-worker:prod
docker login vm-registry.ipic.kz
docker push vm-registry.ipic.kz/airflow-worker:prod
