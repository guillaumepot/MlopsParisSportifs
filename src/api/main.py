"""
API - Main file
"""

"""
libraries
"""
from fastapi import FastAPI, Header,  Request
from api_variables import available_championships, current_season, path_data_clean
from api_functions import checkApiVersion

"""
API declaration
"""
app = FastAPI(
    title="Paris Sportifs API",
    description="Datascientest nov23 Paris sportifs project - API ",
    version="development",
    openapi_tags=[
        {
            'name': 'home',
            'description': 'default functions'
        },
        {
            'name': 'auth',
            'description': 'auth related functions'

        },
        {
            'name': 'user',
            'description': 'user related functions'
        },
        {
            'name': 'admin',
            'description': 'admin related functions'
        }
    ]
)


######################################################################################

"""
API Logger
"""
import logging

# Logger
logger = logging.getLogger("uvicorn")
# Define log level
logger.setLevel(logging.INFO)
# Create log file
handler = logging.FileHandler('api.log')
# Set handler level
handler.setLevel(logging.INFO)
# Add logger to handler
logger.addHandler(handler)


@app.middleware("http")
async def log_middleware(request: Request, call_next):
    """
    Middleware function that logs incoming requests and outgoing responses.

    Args:
        request (Request): The incoming request object.
        call_next (Callable): The next middleware or endpoint to call.

    Returns:
        Response: The response object.
    """
    headers = {k: v for k, v in request.headers.items() if k.lower() not in ['authorization']}
    origin = request.client.host if request.client else 'Unknown'
    logger.info(f"\n\n Received request: {request.method}" \
                f"\n Request: {request.url}" \
                f"\n Origin: {origin}")
    logger.info(f"Headers: {headers}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response

######################################################################################
    
"""
home routes
"""
# /status route
@app.get("/status", name="status", tags=['home'])
@checkApiVersion()
async def getStatus(api_version: str = Header(...)):
    """
    Get the status of the API.

    Parameters:
    - api_version (str): The version of the API.

    Returns:
    - dict: A dictionary containing the status and version of the API.
    """
    # return
    return {"status": "API en ligne", "version": api_version}





# /available_championships route
@app.get("/available_championships", name="available_championships", tags=['home'])
@checkApiVersion()
async def getCurrentChampionship(api_version: str = Header(...)):
    """
    Get the current championship and available championships.

    Parameters:
    - api_version (str): The version of the API.

    Returns:
    - dict: A dictionary containing the current season and available championships.
    """
    available_championship_and_teams = {}
    for championship in available_championships:

        # Get the team list for the championship
        with open(f"{path_data_clean}{championship}/available_teams.json", "r") as file:
            available_championship_and_teams[championship] = json.load(file)

    return {"Current Season": current_season,
            "Available Championships": list(available_championship_and_teams.keys()),
            "Available Teams": available_championship_and_teams}


######################################################################################

"""
auth routes
"""
from auth_routes import *
# Auth routes
app.include_router(auth_router, tags=['auth'])

######################################################################################

"""
admin routes
"""
from admin_routes import *
# Admin routes
app.include_router(admin_router, tags=['admin'])

######################################################################################

"""
user routes
"""
from user_routes import *
# User routes
app.include_router(user_router, tags=['user'])

######################################################################################