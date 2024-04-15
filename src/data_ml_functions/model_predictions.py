"""
Model Predictions - script
"""

"""
Libraries
"""
import pandas as pd
from joblib import load
import os


from common_variables import path_data_raw, path_data_clean, path_to_model, risk_aversion_coefficients, championships

"""
Processing Functions
"""
def loadCleanedDatas(championship):
    """
    Load the cleaned data for a specific championship.

    Parameters:
    championship (str): The name of the championship.

    Returns:
    tuple: A tuple containing the statistics for the home team and the away team.
    """
    # Load the cleaned data
    folder = path_data_clean + championship + '/'
    file_home_team = folder + "statsHomeTeam.csv"
    file_away_team = folder + "statsAwayTeam.csv"

    stats_home_team = pd.read_csv(file_home_team)
    stats_away_team = pd.read_csv(file_away_team)
    return stats_home_team, stats_away_team


def createDataToPredict(championship:str, home_team:str, away_team:str) -> pd.DataFrame:
    """
    Create a DataFrame containing the data to predict for a given championship, home team, and away team.

    Parameters:
    championship (str): The name of the championship.
    home_team (str): The name of the home team.
    away_team (str): The name of the away team.

    Returns:
    pd.DataFrame: The DataFrame containing the data to predict.
    """
    stats_home_team, stats_away_team = loadCleanedDatas(championship)

    stats_home_team = stats_home_team[stats_home_team.HomeTeam == home_team].reset_index(drop=True)
    stats_away_team = stats_away_team[stats_away_team.AwayTeam == away_team].reset_index(drop=True)
    
    data_to_predict = pd.concat([stats_home_team, stats_away_team], axis=1)
    data_to_predict.drop(["HomeTeam", "AwayTeam"], axis=1, inplace=True)
    
    return data_to_predict



"""
Prediction Functions
"""
def loadModel(model_to_load):
    """
    Load the trained model from the pickle file.

    Returns:
        The loaded model.
    """
    # Load the model
    loaded_model = load(model_to_load)
    
    return loaded_model



def predictMatchIssue(model_to_load, data_to_predict: pd.DataFrame) -> pd.DataFrame:
    """
    Predicts the probabilities of the full-time result (FTR) for a given match.

    Args:
        data_to_predict (pd.DataFrame): The input data containing the features of the match.
        home_team: The name of the home team.
        away_team: The name of the away team.

    Returns:
        pd.DataFrame: A DataFrame containing the predicted probabilities of the FTR for the match.
            The columns represent the probabilities of the home team winning, a draw, and the away team winning, respectively.
    """
    # Load model
    loaded_model = loadModel(model_to_load)

    # Predict probabilities of FTR
    probabilities = loaded_model.predict_proba(data_to_predict)

    # Create DataFrame
    result_probabilities = pd.DataFrame({
        "Home": probabilities[:, 0],
        "Draw": probabilities[:, 1],
        "Away": probabilities[:, 2]})
                             
    return result_probabilities



def getModelPredictions(championship, home_team, away_team):
    """
    Get the predictions for a match in a given championship.

    Parameters:
    championship (str): The name of the championship.
    home_team (str): The name of the home team.
    away_team (str): The name of the away team.
    user_role (int, optional): The user's role. Defaults to 0.
    user_bankroll (int, optional): The user's bankroll. Defaults to 0.
    user_risk_aversion (str, optional): The user's risk aversion level. Defaults to 'low'.
    odds (list, optional): The odds for the match. Defaults to None.

    Returns:
    dict: The predictions for the match as a JSON object.
    """
    data_to_predict = createDataToPredict(championship, home_team, away_team)

    model_to_load = path_to_model + championship + '_svc.pkl'
    result_probabilities = predictMatchIssue(model_to_load, data_to_predict)

    # DataFrame to JSON
    result_probabilities_json = result_probabilities.to_dict(orient="records")[0]
    
    return result_probabilities_json


"""
Kelly Criterion Functions
"""

def kellyCriterion(result_probabilities, odds:list , user_risk_aversion: str) -> float:
    """
    Calculate the optimal fraction to bet using the Kelly Criterion.

    Parameters:
    probabilities (pd.DataFrame or list): A variable containing the probabilities of each outcome.
    odds (list): A list of odds for each outcome.
    risk_aversion (str): The level of risk aversion.

    Returns:
    float: The optimal fraction to bet.

    """
    # Flatten the DataFrame to a list
    if isinstance(result_probabilities, pd.DataFrame):
        probabilities = result_probabilities.values.flatten().tolist()

    elif isinstance(result_probabilities, list):
        probabilities = result_probabilities

    else:
        raise ValueError("The result probabilities must be a DataFrame or a list.")

    b = [odd - 1 for odd in odds]  # Convert odds to payout ratios
    q = [1 - prob for prob in probabilities]  # Loss probabilities

    kelly_fractions = [(b[i] * probabilities[i] - q[i]) / b[i] for i in range(len(probabilities))]
    optimal_fraction = max(kelly_fractions)

    risk_aversion_coefficient = risk_aversion_coefficients[user_risk_aversion]
    optimal_fraction *= risk_aversion_coefficient

    return optimal_fraction



def generateBetAdvises(result_probabilities, user_bankroll, user_risk_aversion, odds):
    """
    Generate betting advises based on the given parameters.

    Args:
        result_probabilities (list): List of probabilities for each outcome.
        bankroll (float): The amount of money available for betting.
        risk_aversion (float): The level of risk aversion of the bettor.
        odds (list): List of odds for each outcome.

    Returns:
        dict: A dictionary containing the optimal bet size.

    """
    optimal_fraction = kellyCriterion(result_probabilities, odds, user_risk_aversion)
    optimal_bet_size = round(optimal_fraction * user_bankroll, 2)

    return optimal_bet_size



"""
Meta Function
"""
def getPredictionsOnCalendar():
    """
    Get predictions for each match in the calendar.

    This function reads the calendar data for each championship, iterates over each match,
    and calls the getModelPredictions function to get the predictions for the match.
    The predictions are then appended to the dataframe and saved back to the calendar file.

    Parameters:
    None

    Returns:
    None
    """
    for championship in championships:
        championship_calendar_path = os.path.join(path_data_clean, championship, "odds.csv")
        df_calendar = pd.read_csv(championship_calendar_path)
        predictions = []

        for index, row in df_calendar.iterrows():
            home_team = row["HomeTeam"]
            away_team = row["AwayTeam"]

            prediction = getModelPredictions(championship, home_team, away_team)
            prediction = {k: round(v, 2) for k, v in prediction.items()}
            predictions.append(prediction)

        # Add the predictions to the dataframe
        df_calendar['predictions'] = predictions

        # Extract values and create new columns
        df_calendar['pred_home'] = df_calendar['predictions'].apply(lambda x: x['Home'])
        df_calendar['pred_draw'] = df_calendar['predictions'].apply(lambda x: x['Draw'])
        df_calendar['pred_away'] = df_calendar['predictions'].apply(lambda x: x['Away'])

        # Drop the original 'predictions' column
        df_calendar = df_calendar.drop(columns=['predictions'])

        # Save the dataframe back to the csv file
        df_calendar.to_csv(championship_calendar_path, index=False)




"""
Not used - New functions - Test purposes
"""
def createMatchHistoryWithPredictions(championship:str, path_data_clean = path_data_clean):
    """
    Create or update the match history with predictions for a given championship.

    Parameters:
    championship (str): The name of the championship.
    path_data_clean (str): The path to the clean data directory. Defaults to path_data_clean.

    Returns:
    None
    """
    # Check if the file exists
    if not os.path.exists(path_data_clean + championship + '/match_history.csv'):
        # Create an empty DataFrame with the specified columns
        df_match_history = pd.DataFrame(columns=['Date', 'HomeTeam', 'AwayTeam', 'FTR', 'Avg_H', 'Avg_D', 'Avg_A', 'pred_home', 'pred_draw', 'pred_away'])
        # Save the DataFrame to a csv file
        df_match_history.to_csv(path_data_clean + championship + '/match_history.csv', index=False)
    else:
        # Load the file
        df_match_history = pd.read_csv(path_data_clean + championship + '/match_history.csv')

    # Load odds (with predictions)
    df_odds = pd.read_csv(path_data_clean + championship + '/odds.csv')

    # Concatenate datas
    df_match_history = pd.concat([df_match_history, df_odds], ignore_index=True)

    from data_preprocessing_matches import exportMatchResults
    df_new_history = exportMatchResults(championship, path_data_raw = path_data_raw)

    # Update df_match_history with new datas
    df_match_history.set_index(['Date', 'HomeTeam', 'AwayTeam'], inplace=True)
    df_new_history.set_index(['Date', 'HomeTeam', 'AwayTeam'], inplace=True)
    df_match_history['FTR'].update(df_new_history['FTR'])

    df_match_history.reset_index(inplace=True)
    df_match_history.drop_duplicates(subset=['Date', 'HomeTeam', 'AwayTeam'],keep='last', inplace=True)

    # Save the DataFrame to a csv file
    df_match_history.to_csv(path_data_clean + championship + '/match_history.csv', index=False)