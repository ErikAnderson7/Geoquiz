#!/bin/bash

echo "Building the application image"

docker build -t --no-cache erikanderson7/geoquiz ./application/backend

echo "Pushing the image to docker hub"

docker push erikanderson7/geoquiz