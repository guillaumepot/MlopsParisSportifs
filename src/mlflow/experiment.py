"""
Mlflow - Experiment file
"""

"""
Libraries
"""
from mlflow import MlflowClient
import mlflow
import datetime
import base64

from experiment_variables import tracking_uri, championships, minimal_accuracy
from train_model import trainAndEvaluateModel


"""
Mlflow
"""

for championship in championships:

    # Define tracking_uri
    mlflow.set_tracking_uri(tracking_uri)
    client = MlflowClient()

    # Train model & get model datas
    model, best_params, metrics, conf_matrix_img, X_test = trainAndEvaluateModel(championship)

    # Retrain the best model with all the data
    features, target = trainAndEvaluateModel(championship, test_size=0)
    model.fit(features, target)

    # Get some informations for mlflow
    model_name = model.__class__.__name__
    conf_matrix_img_decoded = base64.b64decode(conf_matrix_img)
    with open("confusion_matrix.png", 'wb') as f:
        f.write(conf_matrix_img_decoded)


    # Define mlflow meta datas
    mlflow.set_experiment("train_" + championship)
    run_name = "Train_" + championship + "_" + model_name + "_" + datetime.datetime.now().strftime("%Y%m%d")
    artifact_path = "artifacts_" + championship + "_" + model_name

    # Store information in tracking server
    with mlflow.start_run(run_name=run_name) as run:
        for key, value in best_params.items():
            mlflow.log_param(key, value)
        mlflow.log_metrics(metrics)
        mlflow.log_artifact("confusion_matrix.png")
        mlflow.sklearn.log_model(sk_model=model,
                                input_example=X_test,
                                artifact_path=artifact_path,
                                registered_model_name=f"{championship}_svc")
        
        # Tag the model based on its accuracy
        if metrics['accuracy'] > minimal_accuracy:
            client.set_tag(run.info.run_id, "quality", "good")
        else:
            client.set_tag(run.info.run_id, "quality", "bad")