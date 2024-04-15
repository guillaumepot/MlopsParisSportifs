#!/bin/bash
# Stop API container
cd ./src/api
./uninstall_api.sh

# Stop Streamlit container
cd ../streamlit
./uninstall_streamlit.sh

# Stop MLflow tracking server container
cd ../mlflow/tracking_server
./uninstall_tracking.sh

# Stop Airflow container
cd ../../airflow
./uninstall_airflow.sh


# Cleaning the repo
cd ../../
git stash && git stash clear