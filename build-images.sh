#!/bin/bash

if [ "$#" == "0" ]
    then
    echo "Please provide image tag"
    exit 1
fi

echo "Building Geoquiz image"
docker build -t erikanderson7/geoquiz:$1 ./application/geoquiz --no-cache

echo "Building Geoquiz-multiplayer image"
docker build -t erikanderson7/geoquiz-multiplayer:$1 ./application/multiplayer --no-cache

echo "Building Geoquiz-db image"
docker build -t erikanderson7/geoquiz-db:$1 ./application/db --no-cache

echo "Pushing images to docker hub"
docker push erikanderson7/geoquiz:$1
docker push erikanderson7/geoquiz-multiplayer:$1
docker push erikanderson7/geoquiz-db:$1