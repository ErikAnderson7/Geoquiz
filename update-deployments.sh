#!/bin/bash

echo "Starting update of Geoquiz and Multiplayer Deployments"

kubectl set image deployments/geoquiz geoquiz=erikanderson7/geoquiz:latest
kubectl set image deployments/geoquiz-multiplayer geoquiz-multiplayer=erikanderson7/geoquiz-multiplayer:latest
