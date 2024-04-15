"""
Mlflow - Model registry
"""

"""
Libraries
"""
from mlflow import MlflowClient
import mlflow
from joblib import load, dump
import os

from experiment_variables import tracking_uri, minimal_accuracy, path_to_model


"""
Mlflow - mlruns uri
"""
# Set the tracking uri
mlflow.set_tracking_uri(tracking_uri)

# Create an MlflowClient
client = MlflowClient()

# List all registered models
registered_models = client.search_registered_models()


"""
Tag model and set production alias on best model for each chapionship
"""

def main():

    # Get model info (for each registered model)
    for model in registered_models:
        # Initialize best accuracy and model
        best_accuracy = 0
        best_model = None


        # List to store good models (accuracy > minimal_accuracy)
        good_models = []
        is_good_model = False


        # Get the name of the model
        model_name = model.name
        # Get the details of the model
        model_details = client.get_registered_model(name=model_name)
        # Get the versions of the model
        model_versions = model_details.latest_versions



        
        # For each version of the model
        for model_version in model_versions:
            # Get the version number
            version = model_version.version
            # Get the run ID of the version
            run_id = model_version.run_id
            # Get the metrics of the run
            metrics = client.get_run(run_id).data.metrics
            client.set_model_version_tag(name=model_name, version=version, key='accuracy', value=format(metrics.get('accuracy', 0), '.2f'))



            # Tag Model Versions (good or bad depending accuracy)
            # Check if accuracy is less than defined minimal accuracy
            if metrics.get('accuracy', 0) < minimal_accuracy:
                # Tag the model version as 'bad'
                client.set_model_version_tag(name=model_name, version=version, key='quality', value='bad')
            else:
                # Tag the model version as 'good'
                client.set_model_version_tag(name=model_name, version=version, key='quality', value='good')

                # Add the model to the good models list (with model path)
                model_path = os.path.relpath(client.get_model_version_download_uri(name=model_name, version=version))
                model_path = os.path.join(model_path, "model.pkl")


            accuracy = metrics.get('accuracy', 0)
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_model = (model_name, version, accuracy, model_path)
                client.set_registered_model_alias(best_model[0], "Production", version)



             # If a good model was found, save it
            if best_model is not None:
                model_name, version, accuracy, model_path = best_model
                print(f"Model {model_name} with version {version} and accuracy {format(accuracy, '.2f')} is good")
                # Save the model
                model = load(model_path)
                dump(model, os.path.join(path_to_model, f"{model_name}.pkl"))
                print(f"Model {model_name} with version {version} and accuracy {format(accuracy, '.2f')} saved to {path_to_model}")
                # Tag the model version as 'production'


            else:
                print(f"No good model found for {model_name}")
        

if __name__ == '__main__':
    main()