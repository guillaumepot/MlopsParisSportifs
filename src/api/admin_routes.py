"""
Routes 'admin'
"""

"""
Libraries
"""
from fastapi import APIRouter, Header, Depends
import json

# Authentification
from auth_routes import get_current_user

# Variables
from api_variables import UserDatas, allowed_type_risk, admin_role, allowed_roles_values, user_database

# Common functions
from api_functions import checkApiVersion, loadUserDatabase, getUserDatas, checkIfUserExists, userIndex, updateUserDatabase

# HTTPException
from api_variables import not_an_admin, wrong_role_value, error_allowed_risk

"""
Admin Router
"""
admin_router = APIRouter()

"""
Admin routes
"""
# /admin/delete/user
@admin_router.delete("/admin/delete/user/{user_to_delete:str}", name="delete_user", tags=['admin'])
@checkApiVersion()
async def callDeleteUser(
    user_to_delete: str, 
    api_version: str = Header(...), 
    current_user: str = Depends(get_current_user)):
    """
    Deletes a user from the user database.

    Args:
        user_to_delete (str): The username of the user to delete.
        api_version (str): The version of the API being used.
        current_user (str): The username of the current user making the request.

    Returns:
        dict: A dictionary containing a message indicating that the user has been deleted.
    """    
    # Load existing user datas from user_database (common function)
    user_data = loadUserDatabase()

    # Admin permissions check (common function)
    user_datas = getUserDatas(current_user)
    if user_datas["role"] is None or user_datas["role"] != admin_role:
        raise not_an_admin

    # Check if username (user_to_delete) exists (common function)
    checkIfUserExists(user_to_delete, reverted = True)

    # Find the unique id of the user (common function)
    user_index = userIndex(current_user = user_to_delete)

    # Delete user
    del user_data[user_index]

    # Write json user database file
    with open(user_database, "w") as file:
        json.dump(user_data, file, indent=4)

    return {"message": f"User {user_to_delete} deleted"}


# /admin/change/user
@admin_router.put("/admin/change/{user_to_change:str}", name="change_user", tags=['admin'])
@checkApiVersion()
async def callChangeUserDatas(
    user: UserDatas,
    user_to_change: str,
    api_version: str = Header(...), 
    current_user: str = Depends(get_current_user)):
    """
    Change the user data for the specified user.

    Parameters:
    - user (UserDatas): The new user data.
    - user_to_change (str): The username of the user to be changed.
    - api_version (str): The version of the API.
    - current_user (str): The username of the current user.

    Returns:
    - dict: A dictionary containing a message indicating that the user data has been changed.
    """
    # Load existing user datas from user_database (common function)
    user_data = loadUserDatabase()

    # Admin permissions check (common function)
    user_datas = getUserDatas(current_user)
    if user_datas["role"] is None or user_datas["role"] != admin_role:
        raise not_an_admin

    # Check if username (user_to_change) exists (common function)
    checkIfUserExists(user_to_change, reverted = True)

    # Find the unique id of the user (common function)
    user_index = userIndex(current_user = user_to_change)


    # Change user datas
    if user.new_username is not None:
        user_data[user_index]["username"] = user.new_username

    if user.new_bankroll is not None:
        user_data[user_index]["bankroll"] = user.new_bankroll

    if user.new_risk is not None:
        # Check if the risk level is allowed
        if user.new_risk not in allowed_type_risk:
            raise error_allowed_risk    
        user_data[user_index]["risk"] = user.new_risk
    
    if user.new_role is not None:
        # Check if the role level is allowed
        if user.new_role not in allowed_roles_values:
            raise wrong_role_value
        user_data[user_index]["role"] = user.new_role

    # Update user password (common function)
    updateUserDatabase(user_data)

    return {"message": f"User {user_to_change} datas changed."}