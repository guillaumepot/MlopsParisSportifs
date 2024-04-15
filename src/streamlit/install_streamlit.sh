#!/bin/bash

# Building images
docker build -t paris_sportifs_streamlit:latest -f ./Dockerfile.streamlit .

# Start containers
docker-compose -f docker-compose_streamlit.yaml up -d
echo -e "Streamlit container started"