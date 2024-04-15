"""
Train & evaluate Model - script
"""

"""
Libraries
"""
import pandas as pd
import time
import pickle
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix

# Confusion matrix related libraries
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64


from common_variables import path_data_clean, grid

"""
Train model functions
"""
def loadDatasTrainModel(path_data_clean, championship:str):
    """
    Load the training data for the model.

    Returns:
        data (pandas.DataFrame): The loaded training data.
    """
    path_training_datas = path_data_clean + championship + "/"
    data = pd.read_csv(path_training_datas + "match_data_for_modeling.csv")
    return data



def splitDatasTrainModel(data, test_size, random_state = 42):
    """

    """
    # Split the data into features (X) and target (y)
    features = data.drop(["FTR", "FTR_encoded", "Date", "HomeTeam", "AwayTeam" ], axis=1)
    target = data['FTR_encoded']

        
    if test_size == 0:
        return features, target
    
    # Calculate the index at which to split the data
    test_size = int(len(features) * test_size)

    # Split the data into training and test sets
    X_train, X_test = features[:-test_size], features[-test_size:]
    y_train, y_test = target[:-test_size], target[-test_size:]


    return X_train, X_test, y_train, y_test



def trainModel(X_train, y_train, grid=grid):
    """
    Train the model using the given training data.

    Parameters:
    X_train (array-like): The input features for training.
    y_train (array-like): The target variable for training.
    Train the model using the given training data.

    Parameters:
    X_train (array-like): The input features for training.
    y_train (array-like): The target variable for training.

    Returns:
    model: The trained model.
    best_params (dict): The best parameters found during training.
    training_time (float): The time taken for training in seconds.
    """
    start_time = time.time()

    # Train the model
    grid.fit(X_train, y_train)
    best_params = grid.best_params_
    model = grid.best_estimator_

    end_time = time.time()
    training_time = end_time - start_time


    return model, best_params, training_time


"""
Evaluate model functions
"""
def evaluateModel(model, X_test, y_test):
    """
    Evaluate the performance of a trained model on test data.

    Parameters:
    model_path (str): The path to the directory containing the trained model.
    championship (str): The name of the championship.
    X_test (array-like): The test data features.
    y_test (array-like): The true labels for the test data.

    Returns:
    dict: A dictionary containing the evaluation metrics, including accuracy, recall, F1 score, and confusion matrix.
    """
    # Get y_pred
    y_pred = model.predict(X_test)

    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred, average='macro')
    f1 = f1_score(y_test, y_pred, average='macro')



    conf_matrix = confusion_matrix(y_test, y_pred)
    # Create a figure for the confusion matrix
    fig, ax = plt.subplots()
    sns.heatmap(conf_matrix, annot=True, ax=ax, cmap='Blues')
    ax.set_xlabel('Predicted labels')
    ax.set_ylabel('True labels')
    ax.set_title('Confusion Matrix')

    # Save the figure as an image in a buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Convert the image to base64 and log it as an artifact
    conf_matrix_img = base64.b64encode(buf.read())

    metrics = {"accuracy": accuracy, "recall": recall, "f1": f1}    
    return metrics, conf_matrix_img


"""
SaveModel function
"""
def saveModel(model, model_to_save_path):
    """
    Save the trained model to a file.
    
    Parameters:
        model (object): The trained model object to be saved.
    """
    with open(model_to_save_path, 'wb') as file:
        pickle.dump(model, file)


"""
Meta function
"""
def trainAndEvaluateModel(championship, test_size=0.2):
    """
    Trains and evaluates a machine learning model.

    Parameters:
    - championship (str): The name of the championship.
    - test_size (float): The proportion of the dataset to include in the test split.

    Returns:
    If test_size > 0:
    - model: The trained machine learning model.
    - best_params: The best parameters found during training.
    - metrics: The evaluation metrics of the model.
    - conf_matrix_img: The image of the confusion matrix.
    - X_test: The test dataset.

    If test_size <= 0:
    - features: The features of the dataset.
    - target: The target variable of the dataset.
    """
    # Load & split the training data
    data = loadDatasTrainModel(path_data_clean, championship)

    if test_size > 0:
        X_train, X_test, y_train, y_test = splitDatasTrainModel(data, test_size)
        # Train the model
        model, best_params, _ = trainModel(X_train, y_train)
        # Evaluate the model
        metrics, conf_matrix_img = evaluateModel(model, X_test, y_test)
        
        return model, best_params, metrics, conf_matrix_img, X_test

    else:
        features, target = splitDatasTrainModel(data, test_size)
        return features, target