#!/bin/bash

echo "Building new test environment"

docker-compose up -d --build

echo "Environment creation finished"
echo "Visit: http://localhost:5001 (Normal)"
echo "       http://localhost:5001/Statistics (Statistics)"
echo "       http://localhost:5002 (Multiplayer)"  
