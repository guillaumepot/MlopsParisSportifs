#!/bin/bash

# Stop containers
docker-compose -f docker-compose_tracking.yaml down

# Remove images
docker rmi paris_sportifs_mlflow_tracking_server:latest