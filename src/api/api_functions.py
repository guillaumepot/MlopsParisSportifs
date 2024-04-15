"""
API- Common functions
"""

"""
Libraries
"""
import os
import json
import re
import uuid
import pandas as pd
from functools import wraps

# Variables
from api_variables import api_versions, user_database, path_data_clean

# HTTPException
from api_variables import wrong_api_version, incorrect_username, wrong_credentials_error, error_password_strength


"""
Functions
"""
# Check API version function (all routes)
def checkApiVersion():
    """
    Decorator function to check if the API version is valid.

    Args:
        api_versions (list): A list of valid API versions.

    Returns:
        decorator: A decorator function that can be used to wrap other functions.

    Raises:
        HTTPException: If the API version is not valid.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            api_version = kwargs.get('api_version')
            if api_version not in api_versions:
                raise wrong_api_version
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Check password strengh on /signup or /change/password
def verifyPasswordStrength(password: str):
    """
    Verify the strength of a password.

    Args:
        password (str): The password to be verified.

    Returns:
        None
    """
    # Check if the password is at least 8 characters long
    is_long_enough = len(password) >= 8

    # Check if the password contains at least one special character
    has_special_char = re.search(r'[@^/:;?!+*-_]', password) is not None

    # Check if the password contains at least one uppercase letter
    has_uppercase = re.search(r'[A-Z]', password) is not None

    # Check if the password contains at least one lowercase letter
    has_lowercase = re.search(r'[a-z]', password) is not None

    # Check if the password contains at least one digit
    has_digit = re.search(r'\d', password) is not None

    # Strong password if all confditions true
    if is_long_enough and has_special_char and has_uppercase and has_lowercase and has_digit:
        return
    else:
        raise error_password_strength



# Read Json User Database
def loadUserDatabase():
    """
    Load the user database from a file and return all user data.

    Returns:
        dict: A dictionary containing all user data.
    """
    # If the file is empty: Create an empty object to avoid error (empty object :  {})
    if os.stat(user_database).st_size == 0:
        with open(user_database, "w") as file:
            json.dump({}, file, indent=4)

    # Load existing user datas from user_database
    with open(user_database, "r") as file:
        all_user_datas = json.load(file)
                
    return all_user_datas



# Save Json User Database
def updateUserDatabase(user_data_to_save):
    """
    Update the user database with the given user data.

    Parameters:
    user_data_to_save (dict): The user data to be saved in the database.

    Returns:
    None
    """
    all_user_datas = loadUserDatabase()
    
    # Update new datas
    all_user_datas.update(user_data_to_save)


    # Save datas to file
    with open(user_database, "w") as file:
        json.dump(all_user_datas, file, indent=4)



# Check if user exists in Database
def checkIfUserExists(user_to_check, reverted=False):
    """
    Check if a user exists in the user database.

    Parameters:
    - user_to_check (str): The username to check.
    - reverted (bool): If True, check if the user does not exist instead.

    Raises:
    - incorrect_username: If the user exists (or does not exist if reverted=True).
    Check if a user exists in the user database.

    Parameters:
    - user_to_check (str): The username to check.
    - reverted (bool): If True, check if the user does not exist instead.

    Raises:
    - incorrect_username: If the user exists (or does not exist if reverted=True).

    """
    all_user_datas = loadUserDatabase()

    if reverted:
        # Check if user exists (reverted)
        for user_key in all_user_datas:
            if user_to_check == all_user_datas[user_key]["username"]:
                return
        raise incorrect_username


    # Check if user exists
    for user_key in all_user_datas:
        if user_to_check == all_user_datas[user_key]["username"]:
            raise incorrect_username



# Get current user datas
def getUserDatas(user_datas_to_get, with_password=False):
    """
    Get user data based on the provided username.

    Args:
        user_datas_to_get (str): The username of the user to retrieve data for.
        with_password (bool, optional): Whether to include the password in the returned data. Defaults to False.

    Returns:
        dict: A dictionary containing the user data, including username, role, bankroll, and risk. If `with_password` is True, the dictionary will also include the password.

    Raises:
        wrong_credentials_error: If the provided username does not exist in the user database.
    """
    all_user_datas = loadUserDatabase()

    for user_key in all_user_datas:
        if user_datas_to_get == all_user_datas[user_key]["username"]:
            user_datas_to_return = {
                "username": all_user_datas[user_key]["username"],
                "role": all_user_datas[user_key]["role"],
                "bankroll": all_user_datas[user_key]["bankroll"],
                "risk": all_user_datas[user_key]["risk"]}

            if with_password:
                user_datas_to_return["password"] = all_user_datas[user_key]["password"]


            return user_datas_to_return
        
    raise wrong_credentials_error



# Generate index for new user
def userIndex(current_user = None, new = False):
    """
    Get the index of the user in the user database.

    Parameters:
    current_user (str): The username of the user.
    new (bool): Flag indicating whether a new index should be generated.

    Returns:
    str: The index of the user in the user database, or None if the user is not found.
    """
    # Load user datas from JSON file (common function)
    all_user_datas = loadUserDatabase()

    # For signup function (generate new index)
    if new == True:
        user_index = str(uuid.uuid4())
    else:
        # Find the unique id of the user
        user_index = None
        for user_index, user in all_user_datas.items():
            if user["username"] == current_user:
                return user_index

    return user_index



# Get available teams in a championship
def getAvailableTeamsInChampionship(championship):
    """
    Get the list of available teams in a given championship.

    Parameters:
    championship (str): The name of the championship.

    Returns:
    list: The list of available teams in the championship.
    """
    df = pd.read_csv(f'{path_data_clean}{championship}/match_data_for_modeling.csv')
    home_teams = df['HomeTeam'].unique()
    away_teams = df['AwayTeam'].unique()
    chosen_championship_teams = list(set(home_teams) | set(away_teams))
    return chosen_championship_teams