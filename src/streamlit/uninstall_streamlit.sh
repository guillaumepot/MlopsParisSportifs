#!/bin/bash

# Stop containers
docker-compose -f docker-compose_streamlit.yaml down

# Remove images
docker image rm paris_sportifs_streamlit:latest
echo -e "Containers & images removed"