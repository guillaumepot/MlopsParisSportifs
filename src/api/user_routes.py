"""
Routes 'user'
"""

"""
Libraries
"""
import os
import pandas as pd
from fastapi import APIRouter, Header, Depends

# Authentification
from auth_routes import get_current_user
from api_variables import pwd_context

# Variables
from api_variables import available_championships, allowed_type_risk, Teams, path_data_clean

# Common functions
from api_functions import checkApiVersion, loadUserDatabase, updateUserDatabase, getUserDatas, userIndex, verifyPasswordStrength
from model_predictions import generateBetAdvises

# HTTPException
from api_variables import wrong_championship, wrong_teams_match, incorrect_password, error_allowed_risk, not_a_premium_member



"""
Auth Router
"""
user_router = APIRouter()

"""
Auth routes
"""
# /user_info route
@user_router.get("/user_info", name="user_info", tags=['user'])
@checkApiVersion()
async def callUserInfo(
    api_version: str = Header(...), 
    current_user = Depends(get_current_user)):
    """
    Retrieve user information.

    Parameters:
    - api_version (str): The version of the API being used.
    - current_user: The current user object.

    Returns:
    - User data: The user data retrieved from the database.
    """
    # load user datas (common function)
    return getUserDatas(current_user)



# /championship & calendar route
@user_router.post("/championship/{championship:str}/calendar", name="championship_calendar", tags=['user'])
@checkApiVersion()
async def callShowCalendarAndPredictions(
    championship: str, 
    api_version: str = Header(...),
    current_user: str = Depends(get_current_user)):
    """
    Calls the show calendar and predictions function for a specific championship.

    Parameters:
    - championship (str): The name of the championship.
    - api_version (str): The version of the API.
    - current_user (str): The current user.

    Returns:
    - dict: A dictionary with a message indicating that the calendar function is not implemented yet.
    """
    # Championship control
    if championship not in available_championships:
        raise wrong_championship
    

    # Get user datas
    user_datas = getUserDatas(current_user)
    # Get user role from user_datas
    current_user_role = user_datas["role"]

    # Premium user is redicrected to the show calendar and predictions route
    if current_user_role != 0:
        # Call Calendar & predictions
        calendar_path = path_data_clean + championship + "/odds.csv"

        # Load calendar datas
        if not os.path.exists(calendar_path):
            return {"message": "Calendar not found for this championship"}

        calendar = pd.read_csv(calendar_path)

        current_user_bankroll = user_datas["bankroll"]
        current_user_risk_aversion = user_datas["risk"]
        
        # Create a list to store the bet advices
        bet_advises = []

        # Iterate over each row in the DataFrame
        for index, row in calendar.iterrows():
            # Extract result probabilities and odds for this row
            result_probabilities = [row["pred_home"], row["pred_draw"], row["pred_away"]]
            odds_scrapped = [row["Avg_H"], row["Avg_D"], row["Avg_A"]]
            
            # Calculate the bet advice for this row
            bet_advise = generateBetAdvises(result_probabilities=result_probabilities,
                                            user_bankroll=current_user_bankroll, 
                                            user_risk_aversion=current_user_risk_aversion,
                                            odds=odds_scrapped)
            
            # Add the bet advice to the list
            bet_advises.append(bet_advise)

        # Add the list of bet advices to the DataFrame as a new column
        calendar["bet_advise"] = bet_advises
        calendar = calendar.to_dict(orient='records')
        return calendar


    # Base users
    raise not_a_premium_member
        



# /predict route
@user_router.post("/predict", name="predict", tags=['user'])
@checkApiVersion()
async def callPrediction(
    teams: Teams, 
    api_version: str = Header(...),
    current_user: str = Depends(get_current_user)):
    """
    Calls the prediction API to get match predictions and optimal bet size for a given match.

    Args:
        teams (Teams): The teams participating in the match.
        api_version (str): The version of the API being used.
        current_user (str): The current user making the request.

    Returns:
        dict: A dictionary containing the match predictions and optimal bet size.
    """
    # Championship control
    if teams.championship not in available_championships:
        raise wrong_championship
    

    # Load prediction datas
    path_to_predictions = os.path.join(path_data_clean, teams.championship,  "odds.csv")
    df_predictions = pd.read_csv(path_to_predictions)

    # Teams control
    if df_predictions[(df_predictions.HomeTeam == teams.home_team) & (df_predictions.AwayTeam == teams.away_team)].empty:
        raise wrong_teams_match

    # Get user datas
    #user_datas = getUserDatas(current_user)
    # Get user role from user_datas
    #current_user_role = user_datas["role"]


    # Premium user is redirected to the show calendar and predictions route
    #if current_user_role != 0:
        #return await callShowCalendarAndPredictions(teams.championship, api_version, current_user)


    # Base users
    # Get predictions for the match
    predictions = df_predictions[(df_predictions.HomeTeam == teams.home_team) & (df_predictions.AwayTeam == teams.away_team)]
    predictions = predictions[["Date", "HomeTeam", "AwayTeam", "pred_home", "pred_draw", "pred_away"]]
    predictions = predictions.to_dict(orient='records')
    return predictions




# /change user datas route
@user_router.post("/change/password", name="change_password", tags=['user'])
@checkApiVersion()
async def changePassword(
    current_password: str,
    new_password: str, 
    api_version: str = Header(...), 
    current_user: str = Depends(get_current_user)):
    """
    Change the password of the current user.

    Args:
        current_password (str): The current password of the user.
        new_password (str): The new password to set for the user.
        api_version (str, optional): The version of the API. Defaults to Header(...).
        current_user (str, optional): The current user. Defaults to Depends(get_current_user).

    Returns:
        dict: A dictionary with a message indicating that the password has been changed successfully.
    """
    # Check if the current password if correct (common function)
    user_datas_with_password = getUserDatas(current_user, with_password = True)
    if not pwd_context.verify(current_password, user_datas_with_password["password"]):
        raise incorrect_password

    # Check if password is strong enough
    verifyPasswordStrength(new_password)

    # Change the password
    new_password = pwd_context.hash(new_password)
    user_datas_with_password["password"] = new_password

    # Load existing user datas from user_database (common function)
    user_data = loadUserDatabase()

    # Find the unique id of the user (common function)
    user_index = userIndex(current_user = current_user)

    # Update user password (common function)
    user_data[user_index] = user_datas_with_password
    updateUserDatabase(user_data)

    return {"message": "Password changed successfully"}


# /change user bankroll route
@user_router.post("/change/bankroll", name="change_bankroll", tags=['user'])
@checkApiVersion()
async def changeBankroll(
    new_bankroll: float, 
    api_version: str = Header(...),
    current_user: dict = Depends(get_current_user)):
    """
    Change the bankroll of the current user.

    Parameters:
    - new_bankroll (float): The new bankroll value.
    - api_version (str): The version of the API.
    - current_user (dict): The current user's information.

    Returns:
    - dict: A dictionary with a success message.
    """
    # Change the bankroll
    user_datas = getUserDatas(current_user)
    user_datas["bankroll"] = new_bankroll

    # Load existing user datas from user_database
    user_data = loadUserDatabase()

    # Find the unique id of the user (common function)
    user_index = userIndex(current_user = current_user)

    # Update user bankroll
    user_data[user_index]["bankroll"] = user_datas["bankroll"]
    updateUserDatabase(user_data)

    return {"message": "Bankroll changed successfully"}


# /change user risk route
@user_router.post("/change/risk", name="change_risk", tags=['user'])
@checkApiVersion()
async def changeRisk(
    new_risk: str, 
    api_version: str = Header(...), 
    current_user: dict = Depends(get_current_user)):
    """
    Change the risk level of the current user.

    Parameters:
    - new_risk (str): The new risk level to set for the user.
    - api_version (str): The version of the API being used.
    - current_user (dict): The current user's information.

    Returns:
    A dictionary with a "message" key indicating the success of the operation.
    """
    # Check if the risk level is allowed
    if new_risk not in allowed_type_risk:
        raise error_allowed_risk

    # Change new risk
    user_datas = getUserDatas(current_user)
    user_datas["risk"] = new_risk

    # Load existing user datas from user_database
    user_data = loadUserDatabase()

    # Find the unique id of the user (common function)
    user_index = userIndex(current_user = current_user)

    # Update user risk
    user_data[user_index]["risk"] = user_datas["risk"]
    updateUserDatabase(user_data)

    return {"message": "Risk level changed successfully"}