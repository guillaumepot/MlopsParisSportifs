#!/bin/bash
# Start API container
cd ./src/api
./install_api.sh &
sleep 30

# Start Streamlit container
cd ../streamlit
./install_streamlit.sh &
sleep 30

# Start Airflow container
cd ../airflow 
./install_airflow.sh &
sleep 90


# Start MLflow tracking server container
cd ../mlflow/tracking_server
./install_tracking.sh &

# Show currently working containers
cd ../../../
echo -e "Containers Started:"
docker container ls