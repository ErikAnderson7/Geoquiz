#!/bin/bash

echo "Building new test environment"

docker-compose up -d --build

echo "Environment creation finished"
echo "Visit: http://localhost:5001 (Normal) http://localhost:5002 (Multiplayer) or https://geoquiz.eanderson.me"