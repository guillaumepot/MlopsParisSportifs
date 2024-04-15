#!/bin/bash

# Stop containers
docker-compose -f docker-compose_mlflow_api.yaml down

# Remove images
docker rmi paris_sportifs_mlflow_api_server:latest