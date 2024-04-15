"""
Libraries
"""
import pytest
from datetime import datetime, timedelta
import pandas as pd
from unittest.mock import Mock
import numpy as np

import sys
sys.path.insert(0, '.')
sys.path.append("/src/data_ml_functions/")


"""
Scrap bookmakers odds - test
"""
from scrap_bookmakers_odds import *
from selenium.webdriver.firefox.webdriver import WebDriver

def test_initializeWebDriver():
    driver = None
    try:
        league_url = "https://www.oddsportal.com/football/england/premier-league/"
        driver = initializeWebDriver(league_url)
        assert isinstance(driver, WebDriver)
    except Exception as e:
        pytest.fail(f"Test failed: {str(e)}")
    finally:
        if driver:
            driver.quit()


def test_ConvertOdds():
    assert ConvertOdds("3/1") == 3.0
    assert ConvertOdds("2/1") == 2.0
    assert ConvertOdds("not a fraction") == "not a fraction"


def test_convertDate():
    # Test with "Today, 05 Jan"
    today = datetime.now()
    date_str = f"Today, {today.strftime('%d %b')}"
    expected = today.strftime('%d/%m/%Y')
    assert convertDate(date_str) == expected

    # Test with "Tomorrow, 08 Mar"
    tomorrow = today + timedelta(days=1)
    date_str = f"Tomorrow, {tomorrow.strftime('%d %b')}"
    expected = tomorrow.strftime('%d/%m/%Y')
    assert convertDate(date_str) == expected

    # Test with "25 Apr 2024"
    date_str = "25 Apr 2024"
    expected = "25/04/2024"
    assert convertDate(date_str) == expected

"""
Scrap match history - test
"""
from scrap_match_history import *

def test_scrapMatchHistory():
    good_url = "https://www.football-data.co.uk/"
    bad_url = "https://www.thisurldoesntexist.com/"
    filename = "test.zip"

    # URL is correct
    result_good_url = scrapMatchHistory(good_url, filename)
    assert result_good_url == {"message" : "File downloaded and saved successfully"}

    # URL is incorrect
    with pytest.raises(Exception) as e:
        scrapMatchHistory(bad_url, filename)
    assert "Failed to resolve 'www.thisurldoesntexist.com'" in str(e.value)


"""
Archive data source - test
"""
#


"""
Data preprocessing matches - test
"""
from data_preprocessing_matches import *
import os


def test_getMatchDatas():
    # Create a test DataFrame
    test_datas = {
        'col1': [1, 2, 3],
        'col2': [4, 5, 6]
    }
    df = pd.DataFrame(test_datas)
    df.to_csv('test.csv', index=False)

    # Define parameters for the function
    championship = 'test'
    path_data_raw = ''
    columns_to_keep_for_features = ['col1', 'col2']

    # Call the function with the test parameters
    result = getMatchDatas(championship, path_data_raw, columns_to_keep_for_features)

    # Verify that the result is correct
    assert result.equals(df[columns_to_keep_for_features])

    # Remove the test file
    os.remove('test.csv')



def test_exportMatchResults():
    pass



def test_createFormScore():
    # Test DF
    data = {
        'Date': pd.date_range(start='1/1/2020', periods=5),
        'HomeTeam': ['Team1', 'Team2', 'Team1', 'Team2', 'Team1'],
        'AwayTeam': ['Team2', 'Team1', 'Team2', 'Team1', 'Team2'],
        'FTR': ['H', 'A', 'D', 'H', 'A']}
    match_results = pd.DataFrame(data)    


    result = createFormScore(match_results = match_results)

    assert isinstance(result, pd.DataFrame)
    assert result.shape == (2, 1)
    assert result.loc['Team1', 'FormScore'] == 5
    assert result.loc['Team2', 'FormScore'] == 5



def test_createTeamStats():
    # Create a test DataFrame
    data = {
        'Date': pd.date_range(start='1/1/2020', periods=5),
        'HomeTeam': ['Team1', 'Team2', 'Team1', 'Team2', 'Team1'],
        'AwayTeam': ['Team2', 'Team1', 'Team2', 'Team1', 'Team2'],
        'FTR': ['H', 'A', 'D', 'H', 'A'],
        'FTHG': [2, 1, 0, 3, 1],
        'FTAG': [1, 2, 0, 1, 3]
    }
    match_data = pd.DataFrame(data)

    # Call the function with the test DataFrame
    home_team_stats, away_team_stats = createTeamStats(match_data)

    # Verify that the results are DataFrames
    assert isinstance(home_team_stats, pd.DataFrame)
    assert isinstance(away_team_stats, pd.DataFrame)

    # Verify that the DataFrames have the correct shape
    assert home_team_stats.shape == (2, 7)
    assert away_team_stats.shape == (2, 7)

    # Verify that the aggregated statistics are correct
    assert home_team_stats.loc[home_team_stats['HomeTeam'] == 'Team1', 'TotalWins'].values[0] == 1
    assert away_team_stats.loc[away_team_stats['AwayTeam'] == 'Team2', 'TotalLosses'].values[0] == 1



def test_mergeTeamStatsHomeAway():
    # Create test data
    home_team_stats = pd.DataFrame({
        'HomeTeam': ['Team1', 'Team2'],
        'Stat1_Home': [1, 2],
        'Stat2_Home': [3, 4]})

    away_team_stats = pd.DataFrame({
        'AwayTeam': ['Team1', 'Team2'],
        'Stat1_Away': [5, 6],
        'Stat2_Away': [7, 8]})

    # Call the function with the test data
    result = mergeTeamStatsHomeAway(home_team_stats, away_team_stats)

    # Create the expected DataFrame
    expected = pd.DataFrame({
        'HomeTeam': ['Team1', 'Team2'],
        'Stat1_Home': [1, 2],
        'Stat2_Home': [3, 4],
        'AwayTeam': ['Team1', 'Team2'],
        'Stat1_Away': [5, 6],
        'Stat2_Away': [7, 8]})

    # Verify that the result is as expected
    pd.testing.assert_frame_equal(result, expected)



def test_createGlobalTeamStats():
    # Création de données de test
    team_stats = pd.DataFrame({
        'TotalGoalsScored_Home': [10, 20],
        'TotalGoalsScored_Away': [5, 10],
        'TotalGoalsConceded_Home': [8, 16],
        'TotalGoalsConceded_Away': [4, 8],
        'TotalWins_Home': [3, 6],
        'TotalWins_Away': [2, 4],
        'TotalDraws_Home': [1, 2],
        'TotalDraws_Away': [1, 2],
        'TotalLosses_Home': [1, 2],
        'TotalLosses_Away': [1, 2],
        'TotalMatches_Home': [5, 10],
        'TotalMatches_Away': [5, 10]
    })

    # Appel de la fonction avec les données de test
    result = createGlobalTeamStats(team_stats)

    # Création du DataFrame attendu
    expected = team_stats.copy()
    expected['TotalGoalsScored'] = expected['TotalGoalsScored_Home'] + expected['TotalGoalsScored_Away']
    expected['TotalGoalsConceded'] = expected['TotalGoalsConceded_Home'] + expected['TotalGoalsConceded_Away']
    expected['GoalDifference'] = expected['TotalGoalsScored'] - expected['TotalGoalsConceded']
    expected['TotalPoints'] = 3 * (expected['TotalWins_Home'] + expected['TotalWins_Away']) + (expected['TotalDraws_Home'] + expected['TotalDraws_Away'])
    expected['TotalMatches'] = expected['TotalMatches_Home'] + expected['TotalMatches_Away']
    expected['WinRatio'] = ((expected['TotalWins_Home'] + expected['TotalWins_Away']) / expected['TotalMatches']) * 100
    expected['DrawRatio'] = ((expected['TotalDraws_Home'] + expected['TotalDraws_Away']) / expected['TotalMatches']) * 100
    expected['LossRatio'] = ((expected['TotalLosses_Home'] + expected['TotalLosses_Away']) / expected['TotalMatches']) * 100
    expected['AverageGoalsScored'] = expected['TotalGoalsScored'] / expected['TotalMatches']
    expected['AverageGoalsConceded'] = expected['TotalGoalsConceded'] / expected['TotalMatches']

    # Vérification que le résultat est comme attendu
    pd.testing.assert_frame_equal(result, expected)



def test_createRanking():
    # Create a test DataFrame
    data = {
        'TotalPoints': [10, 20, 30, 40],
        'GoalDifference': [1, 2, 3, 4]
    }
    df = pd.DataFrame(data)

    # Call the createRanking function
    result = createRanking(df)

    # Verify that the resulting DataFrame is correctly sorted
    assert result['TotalPoints'].tolist() == [40, 30, 20, 10]
    assert result['GoalDifference'].tolist() == [4, 3, 2, 1]

    # Verify that the 'Ranking' column has been added and is correct
    assert 'Ranking' in result.columns
    assert result['Ranking'].tolist() == [1, 2, 3, 4]



def test_mergeFormScoreTeamStats():
    # Create DataFrames for the test
    data1 = {
        'HomeTeam': ['Team1', 'Team2', 'Team3', 'Team4'],
        'TotalPoints': [10, 20, 30, 40],
        'GoalDifference': [1, 2, 3, 4]
    }
    df1 = pd.DataFrame(data1)

    data2 = {
        'FormScore': [5, 6, 7, 8]
    }
    df2 = pd.DataFrame(data2, index=['Team1', 'Team2', 'Team3', 'Team4'])

    # Call the mergeFormScoreTeamStats function
    result = mergeFormScoreTeamStats(df1, df2)

    # Verify that the resulting DataFrame is correctly merged
    assert 'FormScore' in result.columns
    assert result['FormScore'].tolist() == [5, 6, 7, 8]



def test_prepareStatsTeam():
    # Create a DataFrame for the test
    data = {
        'HomeTeam': ['Team1', 'Team2'],
        'AwayTeam': ['Team3', 'Team4'],
        'TotalMatches_Home': [1, 2],
        'TotalWins_Home': [1, 2],
        'TotalDraws_Home': [1, 2],
        'TotalLosses_Home': [1, 2],
        'TotalGoalsScored_Home': [1, 2],
        'TotalGoalsConceded_Home': [1, 2],
        'TotalGoalsScored': [1, 2],
        'TotalGoalsConceded': [1, 2],
        'GoalDifference': [1, 2],
        'TotalPoints': [1, 2],
        'TotalMatches': [1, 2],
        'WinRatio': [1, 2],
        'DrawRatio': [1, 2],
        'LossRatio': [1, 2],
        'AverageGoalsScored': [1, 2],
        'AverageGoalsConceded': [1, 2],
        'Ranking': [1, 2],
        'FormScore': [1, 2],
        'TotalMatches_Away': [1, 2],
        'TotalWins_Away': [1, 2],
        'TotalDraws_Away': [1, 2],
        'TotalLosses_Away': [1, 2],
        'TotalGoalsScored_Away': [1, 2],
        'TotalGoalsConceded_Away': [1, 2]
    }
    df = pd.DataFrame(data)

    # Call the prepareStatsTeam function
    statsHomeTeam, statsAwayTeam = prepareStatsTeam(df)

    # Verify that the resulting DataFrames have the correct columns
    assert 'TotalGoalsScored_HomeTeam' in statsHomeTeam.columns
    assert 'TotalGoalsScored_AwayTeam' in statsAwayTeam.columns

    # Verify that the values are correct
    assert statsHomeTeam['TotalGoalsScored_HomeTeam'].tolist() == [1, 2]
    assert statsAwayTeam['TotalGoalsScored_AwayTeam'].tolist() == [1, 2]



def test_createDataToModelisation():
    # Create DataFrames for the test
    data1 = {
        'HomeTeam': ['Team1', 'Team2'],
        'AwayTeam': ['Team3', 'Team4'],
        'FTR': ['H', 'D']
    }
    df1 = pd.DataFrame(data1)

    data2 = {
        'HomeTeam': ['Team1', 'Team2'],
        'TotalGoalsScored_HomeTeam': [1, 2]
    }
    df2 = pd.DataFrame(data2)

    data3 = {
        'AwayTeam': ['Team3', 'Team4'],
        'TotalGoalsScored_AwayTeam': [3, 4]
    }
    df3 = pd.DataFrame(data3)

    # Call the createDataToModelisation function
    result = createDataToModelisation(df1, df2, df3)

    # Verify that the resulting DataFrame is correctly merged
    assert 'TotalGoalsScored_HomeTeam' in result.columns
    assert 'TotalGoalsScored_AwayTeam' in result.columns
    assert result['TotalGoalsScored_HomeTeam'].tolist() == [1, 2]
    assert result['TotalGoalsScored_AwayTeam'].tolist() == [3, 4]

    # Verify that the 'FTR_encoded' column has been added and is correct
    assert 'FTR_encoded' in result.columns
    assert result['FTR_encoded'].tolist() == [0, 1]



def test_exportCleanDatas():
    pass



def test_getMatchOdds():
    pass


"""
Model Predictions - test
"""
from model_predictions import *

def test_loadCleanedDatas():
    pass


def test_createDataToPredict(monkeypatch):
    # Mock the loadCleanedDatas function to return test data
    def mock_loadCleanedDatas(championship):
        home_team = pd.DataFrame({'HomeTeam': ['team1', 'team2'], 'stat1': [1, 2], 'stat2': [3, 4]})
        away_team = pd.DataFrame({'AwayTeam': ['team3', 'team4'], 'stat3': [5, 6], 'stat4': [7, 8]})
        return home_team, away_team

    monkeypatch.setattr('model_predictions.loadCleanedDatas', mock_loadCleanedDatas)

    # Call the function with test inputs
    data_to_predict = createDataToPredict('test_championship', 'team1', 'team3')

    # Check if the returned object is a pandas DataFrame
    assert isinstance(data_to_predict, pd.DataFrame)

    # Check if the data in the DataFrame is correct
    expected_data = pd.DataFrame({'stat1': [1], 'stat2': [3], 'stat3': [5], 'stat4': [7]})
    pd.testing.assert_frame_equal(data_to_predict, expected_data)



def test_loadModel(monkeypatch):
    pass



def test_predictMatchIssue(monkeypatch):
    # Mock the loadModel function to return a mock model
    def mock_loadModel(model_to_load):
        mock_model = Mock()
        mock_model.predict_proba.return_value = np.array([[0.1, 0.2, 0.7]])  # Return a numpy array
        return mock_model

    monkeypatch.setattr('model_predictions.loadModel', mock_loadModel)

    # Create test input data
    data_to_predict = pd.DataFrame({'stat1': [1], 'stat2': [2], 'stat3': [3], 'stat4': [4]})

    # Call the function with test inputs
    result_probabilities = predictMatchIssue('test_model', data_to_predict)

    # Check if the returned object is a pandas DataFrame
    assert isinstance(result_probabilities, pd.DataFrame)

    # Check if the data in the DataFrame is correct
    expected_data = pd.DataFrame({'Home': [0.1], 'Draw': [0.2], 'Away': [0.7]})
    pd.testing.assert_frame_equal(result_probabilities, expected_data)



def test_getModelPredictions():
    pass



def test_kellyCriterion():
    # Define the input parameters
    result_probabilities = pd.DataFrame([0.2, 0.3, 0.5])
    odds = [2.0, 3.0, 5.0]
    user_risk_aversion = 'medium'

    # Define the expected output
    expected_output = 0.375

    # Call the function with the input parameters
    output = kellyCriterion(result_probabilities, odds, user_risk_aversion)

    # Assert that the output is as expected
    assert output == pytest.approx(expected_output), f'Expected {expected_output}, but got {output}'



def test_generateBetAdvises():

    # Define the input parameters
    result_probabilities = [0.65, 0.25, 0.1]
    user_bankroll = 250
    user_risk_aversion = "medium"
    odds = [1.7, 3.5, 2.3]

    expected_optimal_bet_size = 37.5

    assert generateBetAdvises(result_probabilities, user_bankroll, user_risk_aversion, odds) == expected_optimal_bet_size