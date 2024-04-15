"""
Build features from raw datas - script
"""

"""
Libraries
"""
import pandas as pd
import os
import shutil
import numpy as np
import json

from common_variables import path_data_raw, path_data_clean, championships, columns_to_keep_for_features

"""
Pre-processing Functions
"""
def getMatchDatas(championship, path_data_raw=path_data_raw, columns_to_keep_for_features=columns_to_keep_for_features):
    """
    Get the match data from the specified file path and return only the specified columns.

    Parameters:
    path_data_raw (str): The file path to the raw data.
    columns_to_keep_for_features (list): The list of column names to keep for features.

    Returns:
    pandas.DataFrame: The match data with only the specified columns.
    """
    championship_file_path = path_data_raw + championship + '.csv'    
    match_data = pd.read_csv(championship_file_path)
    return match_data[columns_to_keep_for_features]



def exportMatchResults(championship, path_data_raw = path_data_raw):
    """
    Export match results from a given championship.

    Args:
        path_data_raw (str): The path to the raw data directory.
        championship (str): The name of the championship.

    Returns:
        pandas.DataFrame: A DataFrame containing the match results with columns "Date", "HomeTeam", "AwayTeam", "FTR".
    """
    championship_file_path = path_data_raw + championship + '.csv'
    match_results = pd.read_csv(championship_file_path)  
    return match_results[["Date", "HomeTeam", "AwayTeam", "FTR"]]



def createFormScore(match_results: pd.DataFrame, sort='score') -> pd.DataFrame: 
    """
    Calculate the form score for each team based on their recent match results.

    Parameters:
        match_results (pd.DataFrame): The input DataFrame containing match data.
        sort (str, optional): The sorting parameter. Can be either 'team' or 'score'. Defaults to 'score'.

    Returns:
        pd.DataFrame: A DataFrame containing the form score for each team.

    Raises:
        ValueError: If the sort parameter is not 'team' or 'score'.
    """
    # Sort the data by date in descending order
    match_results = match_results.sort_values(by='Date', ascending=False)

    # Initialize a dictionary to store team performances
    team_form = {}

    # Iterate through the data for each team
    for team in match_results['HomeTeam'].unique():

        # Filter the data for the current team
        team_data = match_results[(match_results['HomeTeam'] == team) | (match_results['AwayTeam'] == team)]

        # Select the results of the last 5 matches
        last_five_matches = team_data.head(5)
        
        # Calculate performances over the last 5 matches
        wins = (last_five_matches['FTR'] == 'H').sum()
        draws = (last_five_matches['FTR'] == 'D').sum()
        losses = (last_five_matches['FTR'] == 'A').sum()

        # Calculate the form score
        form_score = (wins * 3) + draws - losses


        # Add the form score to the dictionary
        team_form[team] = form_score


    # Convert the dictionary to a DataFrame for better visualization
    team_form_df = pd.DataFrame.from_dict(team_form, orient='index', columns=['FormScore'])
    team_form_df.index.name = 'Team'

    if sort == 'team':
        team_form_df = team_form_df.sort_index()

    elif sort == 'score':
        team_form_df = team_form_df.sort_values(by='FormScore', ascending=False)
    
    else:
        raise ValueError("The sort parameter must be either 'team' or 'score'.")

    return team_form_df



def createTeamStats(match_data: pd.DataFrame) -> pd.DataFrame:
    """
    Create aggregated statistics for each team based on match data.

    Args:
        match_data (pd.DataFrame): DataFrame containing match data.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: A tuple of two DataFrames. The first DataFrame contains aggregated statistics for home teams, and the second DataFrame contains aggregated statistics for away teams.
    """
    # Group data by home team to calculate aggregated statistics
    home_team_stats = match_data.groupby('HomeTeam').agg(
            TotalMatches=('HomeTeam', 'count'),
            TotalWins=('FTR', lambda x: (x == 'H').sum()),
            TotalDraws=('FTR', lambda x: (x == 'D').sum()),
            TotalLosses=('FTR', lambda x: (x == 'A').sum()),
            TotalGoalsScored=('FTHG', 'sum'),
            TotalGoalsConceded=('FTAG', 'sum')
        ).reset_index()

    
    # Group data by away team to calculate aggregated statistics
    away_team_stats = match_data.groupby('AwayTeam').agg(
            TotalMatches=('AwayTeam', 'count'),
            TotalWins=('FTR', lambda x: (x == 'A').sum()),  # Invert wins and losses
            TotalDraws=('FTR', lambda x: (x == 'D').sum()),
            TotalLosses=('FTR', lambda x: (x == 'H').sum()),
            TotalGoalsScored=('FTAG', 'sum'),
            TotalGoalsConceded=('FTHG', 'sum')  # Invert goals scored and conceded
        ).reset_index()
    

    return home_team_stats, away_team_stats



def mergeTeamStatsHomeAway(home_team_stats: pd.DataFrame, away_team_stats: pd.DataFrame) -> pd.DataFrame:
    """
    Merge home and away team statistics.

    Parameters:
    - home_team_stats: DataFrame containing home team statistics.
    - away_team_stats: DataFrame containing away team statistics.

    Returns:
    - team_stats: DataFrame containing merged home and away team statistics.
    """
    team_stats = pd.merge(home_team_stats, away_team_stats, left_on='HomeTeam', right_on='AwayTeam', suffixes=('_Home', '_Away'))
    return team_stats



def createGlobalTeamStats(team_stats: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates additional indicators based on team statistics.

    Args:
        team_stats (pd.DataFrame): DataFrame containing team statistics.

    Returns:
        pd.DataFrame: DataFrame with additional indicators calculated.
    """
    # Calculate additional indicators
    global_team_stats = team_stats.copy()
    global_team_stats['TotalGoalsScored'] = global_team_stats['TotalGoalsScored_Home'] + global_team_stats['TotalGoalsScored_Away']
    global_team_stats['TotalGoalsConceded'] = global_team_stats['TotalGoalsConceded_Home'] + global_team_stats['TotalGoalsConceded_Away']
    global_team_stats['GoalDifference'] = global_team_stats['TotalGoalsScored'] - global_team_stats['TotalGoalsConceded']    
    global_team_stats['TotalPoints'] = 3 * (global_team_stats['TotalWins_Home'] + global_team_stats['TotalWins_Away']) + (global_team_stats['TotalDraws_Home'] + global_team_stats['TotalDraws_Away'])
    global_team_stats['TotalMatches'] = global_team_stats['TotalMatches_Home'] + global_team_stats['TotalMatches_Away']
    global_team_stats['WinRatio'] = ((global_team_stats['TotalWins_Home'] + global_team_stats['TotalWins_Away']) / global_team_stats['TotalMatches']) * 100
    global_team_stats['DrawRatio'] = ((global_team_stats['TotalDraws_Home'] + global_team_stats['TotalDraws_Away']) / global_team_stats['TotalMatches']) * 100
    global_team_stats['LossRatio'] = ((global_team_stats['TotalLosses_Home'] + global_team_stats['TotalLosses_Away']) / global_team_stats['TotalMatches']) * 100
    global_team_stats['AverageGoalsScored'] = global_team_stats['TotalGoalsScored'] / global_team_stats['TotalMatches']
    global_team_stats['AverageGoalsConceded'] = global_team_stats['TotalGoalsConceded'] / global_team_stats['TotalMatches']
    
    return global_team_stats



def createRanking(global_team_stats: pd.DataFrame) -> pd.DataFrame:
    """
    Adds the team ranking indicator to the existing calculated indicators.

    Args:
        team_stats (pd.DataFrame): DataFrame containing team statistics.

    Returns:
        pd.DataFrame: DataFrame with team ranking indicator added.
    """
    # Sort the DataFrame by TotalPoints then by GoalDifference
    global_team_stats_ranking = global_team_stats.sort_values(by=['TotalPoints', 'GoalDifference'], ascending=False)

    # Reset the DataFrame index to reflect the ranking
    global_team_stats_ranking.reset_index(drop=True, inplace=True)

    # Create a "Classement" column based on the index + 1
    global_team_stats_ranking['Ranking'] = global_team_stats_ranking.index + 1
    
    return global_team_stats_ranking



def mergeFormScoreTeamStats(global_team_stats_ranking: pd.DataFrame, team_form_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merges the team statistics DataFrame with the team form DataFrame.

    Args:
        team_stats (pd.DataFrame): DataFrame containing team statistics.
        team_form_df (pd.DataFrame): DataFrame containing team form scores.

    Returns:
        pd.DataFrame: Merged DataFrame containing both team statistics and form scores.
    """
    score_team_stats = pd.merge(global_team_stats_ranking, team_form_df, left_on='HomeTeam', right_index=True, how='left')

    return score_team_stats



def prepareStatsTeam(score_team_stats: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare the statistics for home team and away team.

    Args:
        home_team_stats (pd.DataFrame): DataFrame containing the statistics for the home team.
        away_team_stats (pd.DataFrame): DataFrame containing the statistics for the away team.

    Returns:
        pd.DataFrame: DataFrame containing the prepared statistics for the home team and away team.
    """
    # statsHomeTeam
    home_rename_dict = {
        'TotalGoalsScored': 'TotalGoalsScored_HomeTeam',
        'TotalGoalsConceded': 'TotalGoalsConceded_HomeTeam',
        'GoalDifference': 'GoalDifference_HomeTeam',
        'TotalPoints': 'TotalPoints_HomeTeam',
        'TotalMatches': 'TotalMatches_HomeTeam',
        'WinRatio': 'WinRatio_HomeTeam', 
        'DrawRatio': 'DrawRatio_HomeTeam',
        'LossRatio': 'LossRatio_HomeTeam',
        'AverageGoalsScored': 'AverageGoalsScored_HomeTeam', 
        'AverageGoalsConceded': 'AverageGoalsConceded_HomeTeam' , 
        'Ranking': 'Ranking_HomeTeam',
        'FormScore': 'FormScore_HomeTeam'}

    statsHomeTeam = score_team_stats[['HomeTeam', 'TotalMatches_Home', 'TotalWins_Home', 'TotalDraws_Home',
                                'TotalLosses_Home', 'TotalGoalsScored_Home', 'TotalGoalsConceded_Home',
                                'TotalGoalsScored', 'TotalGoalsConceded', 'GoalDifference',
                                'TotalPoints', 'TotalMatches', 'WinRatio', 'DrawRatio', 'LossRatio',
                                'AverageGoalsScored', 'AverageGoalsConceded', 'Ranking','FormScore'
                                ]]

    # Add the HomeTeam suffix
    statsHomeTeam = statsHomeTeam.rename(columns=home_rename_dict)


    # statsAwayTeam
    away_rename_dict = {
            'TotalGoalsScored': 'TotalGoalsScored_AwayTeam',
            'TotalGoalsConceded': 'TotalGoalsConceded_AwayTeam',
            'GoalDifference': 'GoalDifference_AwayTeam',
            'TotalPoints': 'TotalPoints_AwayTeam',
            'TotalMatches': 'TotalMatches_AwayTeam',
            'WinRatio': 'WinRatio_AwayTeam', 
            'DrawRatio': 'DrawRatio_AwayTeam',
            'LossRatio': 'LossRatio_AwayTeam',
            'AverageGoalsScored': 'AverageGoalsScored_AwayTeam', 
            'AverageGoalsConceded': 'AverageGoalsConceded_AwayTeam' , 
            'Ranking': 'Ranking_AwayTeam',
            'FormScore': 'FormScore_AwayTeam'}

    statsAwayTeam = score_team_stats[['AwayTeam', 'TotalMatches_Away', 'TotalWins_Away', 'TotalDraws_Away',
                                'TotalLosses_Away', 'TotalGoalsScored_Away', 'TotalGoalsConceded_Away',
                                'TotalGoalsScored', 'TotalGoalsConceded', 'GoalDifference',
                                'TotalPoints', 'TotalMatches', 'WinRatio', 'DrawRatio', 'LossRatio',
                                'AverageGoalsScored', 'AverageGoalsConceded', 'Ranking','FormScore'
                                ]]
        
    # Ajouter le suffixe Away
    statsAwayTeam = statsAwayTeam.rename(columns=away_rename_dict)

    
    return statsHomeTeam, statsAwayTeam



def createDataToModelisation(championship_matches_results: pd.DataFrame,
                             statsHomeTeam: pd.DataFrame,
                             statsAwayTeam: pd.DataFrame) -> pd.DataFrame:
    """
    Create a dataframe for modelization by merging championship matches results, home team statistics, and away team statistics.
    
    Parameters:
        championship_matches_results (pd.DataFrame): DataFrame containing the results of championship matches.
        statsHomeTeam (pd.DataFrame): DataFrame containing the statistics of home teams.
        statsAwayTeam (pd.DataFrame): DataFrame containing the statistics of away teams.
    
    Returns:
        pd.DataFrame: DataFrame containing the merged data for modelization.
    """
    
    final_stats_home = pd.merge(championship_matches_results, statsHomeTeam, on="HomeTeam")
    final_stats_home_away = pd.merge(final_stats_home, statsAwayTeam, on="AwayTeam")

    # Encode target variable 

    ftr_mapping = {
    "H": 0,
    "D": 1,
    "A": 2}

    final_stats_home_away['FTR_encoded'] = final_stats_home_away['FTR'].map(ftr_mapping)
    
    return final_stats_home_away
    

    
def exportCleanDatas(championship, stats_home_team, stats_away_team, final_stats_home_away, path_data_clean=path_data_clean):
    """
    Export the clean data to CSV files.

    Parameters:
    - statsHomeTeam: DataFrame containing statistics for the home team.
    - statsAwayTeam: DataFrame containing statistics for the away team.
    - final_stats_home_away: DataFrame containing final statistics for both home and away teams.

    Returns:
    None
    """
    path_output_for_clean_datas = path_data_clean + championship + '/'

    # Create folders if don't exist
    if not os.path.exists(path_output_for_clean_datas):
        os.makedirs(path_output_for_clean_datas)

    # Save datas
    stats_home_team.to_csv(path_output_for_clean_datas + "statsHomeTeam.csv", index=False)
    stats_away_team.to_csv(path_output_for_clean_datas + "statsAwayTeam.csv", index=False)
    final_stats_home_away.to_csv(path_output_for_clean_datas + "match_data_for_modeling.csv", index=False)



def getMatchOdds(championship, path_data_clean=path_data_clean, path_data_raw=path_data_raw):
    """
    Copy the odds file for a specific championship from the raw data directory to the clean data directory.

    Parameters:
    championship (str): The name of the championship.
    path_data_clean (str): The path to the clean data directory. Defaults to path_data_clean.
    path_data_raw (str): The path to the raw data directory. Defaults to path_data_raw.
    """
    odds_file = os.path.join(path_data_raw, championship + '_odds.csv')
    shutil.copy(odds_file, path_data_clean + championship + '/odds.csv')


def getAvailableTeams(championship: str) -> None:
    """
    Get the list of available teams for a given championship.

    Parameters:
    championship (str): The name of the championship.

    Returns:
    None

    This function reads the match data and odds data for the given championship,
    extracts the home and away teams from both datasets, and returns a list of
    unique teams available in either dataset. The list is then saved to a JSON
    file named 'available_teams.json' in the same directory as the data files.
    """
    available_teams = []

    # Get teams listed in the different match datas
    df_file_odds = pd.read_csv(path_data_clean + championship + '/odds.csv')
    df_file_odds = df_file_odds[["HomeTeam", "AwayTeam"]]
    df_file_match_datas = pd.read_csv(path_data_clean + championship + '/match_data_for_modeling.csv')
    df_file_match_datas = df_file_match_datas[["HomeTeam", "AwayTeam"]]

    # Get unique teams from both dataframes
    teams_odds = np.unique(df_file_odds[["HomeTeam", "AwayTeam"]].values)
    teams_match_datas = np.unique(df_file_match_datas[["HomeTeam", "AwayTeam"]].values)

    # Get the union of both team sets
    available_teams = np.union1d(teams_odds, teams_match_datas)

    # Convert numpy array to list
    available_teams = available_teams.tolist()


    # Save the list to a file
    save_folder = path_data_clean + championship + '/'
    with open(f'{save_folder}available_teams.json', 'w') as f:
        json.dump(available_teams, f)




def preProcessingPipeline() -> None:
    """
    Executes the preprocessing pipeline for a given set of championships.
    
    This function performs a series of data preprocessing steps for each championship in the `championships` list.
    It retrieves match data, exports match results, creates team form scores, calculates team statistics,
    merges team statistics, creates global team statistics, creates rankings, merges form scores with team statistics,
    prepares team statistics for modeling, creates final data for modeling, exports clean data, retrieves match odds,
    and gets available teams.
    
    Note: The `championships` list should be defined before calling this function.
    """
    for championship in championships:
        match_data = getMatchDatas(championship)
        match_results = exportMatchResults(championship)

        team_form_df = createFormScore(match_results, sort='score')

        home_team_stats, away_team_stats = createTeamStats(match_data)
        team_stats = mergeTeamStatsHomeAway(home_team_stats, away_team_stats)
        global_team_stats = createGlobalTeamStats(team_stats)
        global_team_stats_ranking = createRanking(global_team_stats)

        score_team_stats = mergeFormScoreTeamStats(global_team_stats_ranking, team_form_df)
        stats_home_team, stats_away_team = prepareStatsTeam(score_team_stats)

        final_stats_home_away = createDataToModelisation(match_results, stats_home_team, stats_away_team)

        exportCleanDatas(championship, stats_home_team, stats_away_team, final_stats_home_away)
        getMatchOdds(championship)
        
        getAvailableTeams(championship)