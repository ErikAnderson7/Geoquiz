#!/bin/bash

if [ "$#" == "0" ]
    then
    echo "Please provide image tag"
    exit 1
fi

echo "Starting update of Geoquiz and Multiplayer Deployments"

kubectl set image deployments/geoquiz geoquiz=erikanderson7/geoquiz:$1
kubectl set image deployments/geoquiz-multiplayer geoquiz-multiplayer=erikanderson7/geoquiz-multiplayer:$1
