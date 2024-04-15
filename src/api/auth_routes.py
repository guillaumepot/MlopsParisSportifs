"""
Routes 'auth'
"""

"""
Libraries
"""
import jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status, APIRouter


# Authentification variables
from api_variables import oauth2_scheme, pwd_context, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRATION

# Variables
from api_variables import User, allowed_type_risk

# HTTPException
from api_variables import wrong_credentials_error, error_allowed_risk

# Common functions
from api_functions import checkIfUserExists, userIndex, getUserDatas, updateUserDatabase, verifyPasswordStrength


"""
API Router
"""
auth_router = APIRouter()


"""
Auth Routes
"""
# /signup route
@auth_router.post("/signup", name="signup", tags=['auth'])
def UserSignup(user: User):
    """
    Create a new user in the system.

    Args:
        user (User): The user object containing the user information.

    Returns:
        dict: A dictionary with a message indicating the success of the user creation.
    """
    # Check if user exists (common function)
    checkIfUserExists(user.username)

    # Check if password is strong enough
    verifyPasswordStrength(user.password)

    # Generate new user index (common function)
    user_index = userIndex(new=True)

    # Hash the password using Argon2 algorithm
    hashed_password = pwd_context.hash(user.password)

    if user.risk not in allowed_type_risk:
        raise error_allowed_risk

    # Add the new user to database with role: 0 (free user)
    new_user = {user_index: {"username": user.username, "password": hashed_password, "role": 0, "bankroll": user.bankroll, "risk": user.risk}}

    # Add user to database (common function)
    updateUserDatabase(new_user)

    return {"message": "User created successfully"}


############################################################################################################

# Login route
def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Create an access token with the given data and expiration time.

    Args:
        data (dict): The data to be encoded in the access token.
        expires_delta (timedelta, optional): The expiration time for the access token. Defaults to None.

    Returns:
        str: The encoded access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

###

def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Get the current user based on the provided token.

    Parameters:
    - token (str): The authentication token.

    Returns:
    - str: The username of the current user.

    Raises:
    - HTTPException: If the credentials cannot be validated.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"})
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_username = payload.get("sub")
    except Exception as e:
        print(f"An error occurred while decoding the token: {e}")
        raise credentials_exception
    
    return user_username


###

# Route
@auth_router.post("/login", name="login", tags=['auth'])
def userLogin(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticates the user and generates an access token.

    Args:
        form_data (OAuth2PasswordRequestForm): The form data containing the username and password.

    Returns:
        dict: A dictionary containing the access token and token type.
    """

    # Check if the user exists and get the current password in the database
    loaded_username_and_password = getUserDatas(form_data.username, with_password = True)

    # Check if credentials are correct
    if not pwd_context.verify(form_data.password, loaded_username_and_password["password"]):
        raise wrong_credentials_error

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRATION)
    access_token = create_access_token(data={"sub": form_data.username}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}