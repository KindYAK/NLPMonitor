#!/usr/bin/env bash
set -e
cd web
docker build . -f docker/Dockerfile
docker login repo.treescale.com -t repo.treescale.com/biboran/nlpmonitor:prod
docker push repo.treescale.com/biboran/nlpmonitor:prod
