#!/usr/bin/env bash
set -e
cd web
docker build . -f docker/Dockerfile -t vm-registry.ipic.kz/nlpmonitor:prod
docker login vm-registry.ipic.kz
docker push vm-registry.ipic.kz/nlpmonitor:prod
