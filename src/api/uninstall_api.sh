#!/bin/bash

# Stop containers
docker-compose -f docker-compose_api.yaml down

# Remove images
docker image rm paris_sportifs_api:latest
echo -e "Containers & images removed"


# Remove py files
rm ./common_variables.py
rm ./model_predictions.py