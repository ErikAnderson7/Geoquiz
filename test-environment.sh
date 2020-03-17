#!/bin/bash

echo "Building new test environment"

docker system prune -a
docker-compose up -d --build

echo "Environment creation finished"
echo "Visit: http://localhost:5001 or https://geoquiz.eanderson.me"