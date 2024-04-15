#!/bin/bash

# Build mlflow image
docker build -t paris_sportifs_mlflow_tracking_server:latest -f ./Dockerfile.tracking .

# Start containers
docker-compose -f docker-compose_tracking.yaml up -d