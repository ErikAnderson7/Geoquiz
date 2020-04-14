#!/bin/bash

echo "Creating the database credentials..."

kubectl create -f ./kubernetes/postgres-secret.yml
kubectl create -f ./kubernetes/multiplayer-db-secret.yml

echo "Creating the volumes..."

kubectl create -f ./kubernetes/postgres-volume.yml
kubectl create -f ./kubernetes/postgres-volume-claim.yml
kubectl create -f ./kubernetes/multiplayer-db-volume.yml
kubectl create -f ./kubernetes/multiplayer-db-volume-claim.yml

echo "Creating the postgres deployment and service..."

kubectl create -f ./kubernetes/postgres-deployment.yml
kubectl create -f ./kubernetes/postgres-service.yml

echo "Creating the flask deployment and service..."

kubectl create -f ./kubernetes/geoquiz-deployment.yml
kubectl create -f ./kubernetes/geoquiz-service.yml

echo "Creating the multiplayer-db deployment and service..."

kubectl create -f ./kubernetes/multiplayer-db-deployment.yml
kubectl create -f ./kubernetes/multiplayer-db-service.yml

echo "Creating the multiplayer deployment and service..."

kubectl create -f ./kubernetes/multiplayer-deployment.yml
kubectl create -f ./kubernetes/multiplayer-service.yml

echo "Adding the ingress..."

minikube addons enable ingress
kubectl apply -f ./kubernetes/ingress.yml