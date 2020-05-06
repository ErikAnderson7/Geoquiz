# Geoquiz

A Web Application where users can test their knowledge of Geography. Utilizes Javascript on the frontend and Python using Flask for the backend.

![image](https://user-images.githubusercontent.com/29104093/81208330-7d662780-8f94-11ea-871e-b485f70934b0.png)

## Installation

Docker and Docker-Compose are required, Kubernetes is optional unless you want to deploy to a production environment.

To create a development environment
    
    docker-compose up -d --build

To deploy to Kubernetes run the deploy script

    ./deploy.sh
