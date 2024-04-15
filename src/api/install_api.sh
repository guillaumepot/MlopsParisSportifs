#!/bin/bash


# Get py files
cp -r ../data_ml_functions/common_variables.py .
cp -r ../data_ml_functions/model_predictions.py .

# Building images
docker build -t paris_sportifs_api:latest -f ./Dockerfile.api .

# Start containers
docker-compose -f docker-compose_api.yaml up -d