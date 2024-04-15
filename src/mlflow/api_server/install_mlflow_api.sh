#!/bin/bash

# Build mlflow image
docker build -t paris_sportifs_mlflow_api_server:latest -f ./Dockerfile.mlflowapi .

# Start containers
docker-compose -f docker-compose_mlflow_api.yaml up -d