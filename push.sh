#!/usr/bin/env bash
set -e
cd web
docker build . -f docker/Dockerfile -t 109.233.109.111:5000/nlpmonitor:prod
docker login 109.233.109.111:5000
docker push 109.233.109.111:5000/nlpmonitor:prod
