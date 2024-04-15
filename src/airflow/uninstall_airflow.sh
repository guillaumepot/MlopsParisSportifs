#!/bin/bash

# Stop containers
docker-compose -f docker-compose_airflow.yaml down

# Remove containers
docker container rm \
> nov23_continu_mlops_paris_sportifs_airflow-scheduler_1 \
> nov23_continu_mlops_paris_sportifs_airflow-worker_1 \
> nov23_continu_mlops_paris_sportifs_airflow-triggerer_1 \
> nov23_continu_mlops_paris_sportifs_airflow-webserver_1 \
> nov23_continu_mlops_paris_sportifs_airflow-init_1 \
> nov23_continu_mlops_paris_sportifs_redis_1 \
> nov23_continu_mlops_paris_sportifs_postgres_1

# Remove images
docker rmi postgres:13 redis:latest
docker rmi mlops-airflow-python3.10:latest

echo -e "Containers & images succesfully deleted"

# Remove copied py files
rm ./dags/common_variables.py
rm ./dags/scrap_bookmakers_odds.py
rm ./dags/scrap_match_history.py
rm ./dags/archive_datas_source.py
rm ./dags/data_preprocessing_matches.py
rm ./dags/model_predictions.py
rm ./dags/train_model.py
rm ./dags/experiment.py
rm ./dags/experiment_variables.py
rm ./dags/model_registry.py