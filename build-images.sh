#!/bin/bash

echo "Building Geoquiz image"
docker build -t erikanderson7/geoquiz ./application/backend --no-cache

echo "Building Geoquiz-multiplayer image"
docker build -t erikanderson7/geoquiz-multiplayer ./application/multiplayer --no-cache

echo "Building Geoquiz-db image"
docker build -t erikanderson7/geoquiz-db ./application/db --no-cache

echo "Pushing images to docker hub"
docker push erikanderson7/geoquiz:latest
docker push erikanderson7/geoquiz-multiplayer:latest
docker push erikanderson7/geoquiz-db:latest