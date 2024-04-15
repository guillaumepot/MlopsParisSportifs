#!/bin/bash


# Get py files
cp ../data_ml_functions/common_variables.py ./dags # common vars
cp ../data_ml_functions/scrap_bookmakers_odds.py ./dags # Dag Scraper
cp ../data_ml_functions/scrap_match_history.py ./dags # Dag Scraper
cp ../data_ml_functions/geckodriver ./dags # GeckoDriver
cp ../data_ml_functions/archive_datas_source.py ./dags # Dag Scraper (archive function)
cp ../data_ml_functions/data_preprocessing_matches.py ./dags # Dag pre-processing
cp ../data_ml_functions/model_predictions.py ./dags # Dag predictions

# Dag train models use bash commands
cp ../mlflow/model_registry.py ./dags # Dag model registry
cp ../mlflow/experiment_variables.py ./dags # Dag train models
cp ../mlflow/experiment.py ./dags # Dag train models
cp ../data_ml_functions/train_model.py ./dags # Dag train models




# Add env variables
echo -e "AIRFLOW_IMAGE_NAME=mlops-airflow-python3.10:latest" > .env
echo -e "AIRFLOW_UID=$(id -u)" >> .env
echo -e "AIRFLOW_GUID=0" >>.env
echo -e "_AIRFLOW_WWW_USER_USERNAME=admin" >> .env
echo -e "_AIRFLOW_WWW_USER_PASSWORD=4dm1N-01" >> .env


# Add folder permissions
#chmod 777 ./airflow/config/ ./airflow/dags/ ./airflow/plugins/ ./airflow/logs/
chmod 777 .

# Build airflow image
docker build -t mlops-airflow-python3.10:latest -f ./Dockerfile.airflow .

# Init Airflow
docker-compose -f docker-compose_airflow.yaml up airflow-init

# Start containers
docker-compose -f docker-compose_airflow.yaml up -d