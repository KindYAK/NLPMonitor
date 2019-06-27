#!/usr/bin/env bash
set -e
docker login 109.233.109.111:5000
docker pull 109.233.109.111:5000/nlpmonitor:prod
