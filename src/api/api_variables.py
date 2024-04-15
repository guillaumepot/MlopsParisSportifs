"""
API - Common variables
"""

"""
Libraries
"""
import os

"""
API infrastructure variables
"""

# User Database path
user_database = os.getenv('USER_DATABASE', '../../storage/database/userDB.json')

# API available versions
api_versions = ["1"]

# User available values (User Databsase)
allowed_type_risk = ["low", "medium", "high"]
allowed_roles_values = [0, 1, 9] # 0 : Free ; 1 : Premium ; 9 : Admin
admin_role = os.getenv('ADMIN_ROLE', 9)
admin_role = int(admin_role)

######################################################################################

# Available seasons & championships
current_season = os.getenv('CURRENT_SEASON')
path_data_clean = os.getenv('PATH_DATA_CLEAN', '../../storage/data/clean/')
available_championships = next(os.walk(path_data_clean))[1] # Get all available championships in the clean data folder


######################################################################################

# Base Models
from pydantic import BaseModel, Field
from typing import Optional

# Used in /predict
class Teams(BaseModel):
    championship: str
    home_team: str
    away_team: str

# Used in /signup
class User(BaseModel):
    username: str
    password: str
    bankroll: float = Field(0, ge=0)  # ge = greater than or equal to
    risk: str = "low"

# Used in admin routes
class UserDatas(BaseModel):
    new_username: Optional[str] = None
    new_bankroll: Optional[float] = None
    new_risk: Optional[str] = None
    new_role: Optional[int] = None

######################################################################################

# Auth variables
from cryptography.fernet import Fernet
# Generate a new secret key
def generateSecretKey():
    return Fernet.generate_key()

SECRET_KEY = generateSecretKey()
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRATION = 60


# Oauth2.0 variables
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
# Encryption algorithm
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
# Oauth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


######################################################################################

# HTTP Exceptions
from fastapi import HTTPException

# 4xx Client Errors
wrong_api_version = HTTPException(status_code=400, detail="Wrong API version")
wrong_championship = HTTPException(status_code=400, detail="Wrong championship")
wrong_teams_match = HTTPException(status_code=400, detail="Wrong teams match")
user_already_exists = HTTPException(status_code=409, detail="Username already exists")  # Conflict
incorrect_password = HTTPException(status_code=401, detail="Incorrect password")  # Unauthorized
not_a_premium_member = HTTPException(status_code=402, detail="You are not a premium member")  # Payment Required

# 5xx Server Errors
error_password_strength = HTTPException(status_code=500, detail="Password must contain at least 8 characters with uppercase and lowercase letters and symbols (@^/:;?!+*-_).")  # Internal Server Error
incorrect_username = HTTPException(status_code=500, detail="Incorrect username")  # Internal Server Error
wrong_credentials_error = HTTPException(status_code=500, detail="Wrong credentials")  # Internal Server Error
not_an_admin = HTTPException(status_code=500, detail="You are not allowed to use these functions")  # Internal Server Error

error_allowed_risk = HTTPException(status_code=500, detail="Allowed risk should be low, medium or high")  # Internal Server Error
wrong_role_value = HTTPException(status_code=500, detail="Role value is not allowed.")  # Internal Server Error