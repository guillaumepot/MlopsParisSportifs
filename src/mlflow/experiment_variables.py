"""
Libraries
"""
import os

"""
Experiment related vars
"""
tracking_uri = os.getenv("TRACKING_URI", '../../storage/mlflow/mlruns/')
minimal_accuracy = float(os.getenv("MINIMAL_ACCURACY", 0.5))
championships = os.getenv("CHAMPIONSHIPS", 'English Premier League,France Ligue 1').split(',')
path_to_model = os.getenv("PATH_TO_MODEL", '../../storage/models/')