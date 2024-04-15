import os
import mlflow
from mlflow import MlflowClient


from experiment_variables import championships


tracking_uri = os.getenv('TRACKING_URI')




# Set the tracking uri
mlflow.set_tracking_uri(tracking_uri)
# Create an MlflowClient
client = MlflowClient()

for championship in championships:
    model_name = f"{championship}_svc"
    model_version = client.get_latest_versions(model_name, stages=["production"])[0]
    model_uri = f"models:/{model_name}/{model_version.version}"
    model = mlflow.pyfunc.load_model(model_uri=model_uri)
