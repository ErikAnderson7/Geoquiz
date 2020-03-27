# CIS598FinalProject

Tutorial for drawing maps with d3
https://medium.com/@andybarefoot/making-a-map-using-d3-js-8aa3637304ee

Tutorial for running Flask apps on Kubernetes
https://testdriven.io/blog/running-flask-on-kubernetes/

To build container image for application:
sudo docker build -t erikanderson7/geoquiz:latest ./application/backend --no-cache

To push the image to docker hub:
sudo docker push erikanderson7/geoquiz:latest

Get into dev database:
sudo docker exec -it cis598finalproject_postgres_1 psql -U postgres
Get into prod db:
kubectl get pods
copy the postgres pod name
kubectl exec -it {postgres pod name} -- psql -U c2FtcGxl --password

To Update the flask deployment on Kubernetes without killing everything:
kubectl kill deployment flask
kubectl create -f ./kubernetes/flask-deployment.yml