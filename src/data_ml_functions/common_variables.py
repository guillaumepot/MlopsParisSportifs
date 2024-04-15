"""
Libraries
"""
import os


###############################################################################################################################

"""
Common vars to all functions
"""

# Path to data sources in storage
path_data_source = os.getenv("PATH_DATA_SOURCE", "../../storage/data/source/") # Scraped datas stored here
path_data_archives = os.getenv("PATH_DATA_ARCHIVES", "../../storage/data/archives/") # Archives form scrap stored here
path_data_raw = os.getenv("PATH_DATA_RAW", '../../storage/data/raw/') # Raw data corresponding to unzip files from source
path_data_clean = os.getenv("PATH_DATA_CLEAN", '../../storage/data/clean/') # Clean datas (pre-processed datas) stored here


# Path to models in storage
path_to_model = os.getenv("PATH_TO_MODEL", '../../storage/models/')


 # List of available championships the app can handle
championships = os.getenv("CHAMPIONSHIPS", 'English Premier League,France Ligue 1').split(',')


###############################################################################################################################

"""
These vars are used for scraping functions - Match histories
"""

# Current season
current_season = os.getenv("CURRENT_SEASON", '2324')


### Scrap match histories is base on football-data.co.uk website who provides clean csv files for all leagues, all seasons
base_url = "https://www.football-data.co.uk/"

main_leagues_url = base_url + "mmz4281/"
other_leagues_url = base_url + "new/new_leagues_data.xlsx"

# Leagues URLs
main_leagues_current_season_url = main_leagues_url + current_season + "/data.zip"
other_leagues_current_season_url = base_url + "new/new_leagues_data.xlsx" # Same as other_leagues_url


# Filenames
main_leagues_filename = path_data_source + "main_leagues_data.zip" # Used for main leagues match histories scraping
other_leagues_filename = path_data_source + "other_leagues_data.xlsx" # Used for other leagues match histories scraping

# Filename dictionnaries
    # Scraped file names should be changed to the following names
main_leagues_dictionary = {'B1': 'Belgian Pro League',
                           'D1': 'Germany Bundesliga 1',
                           'D2': 'Germany Bundesliga 2',
                           'E0': 'English Premier League',
                           'E1': 'EFL Championship',
                           'E2': 'EFL League One',
                           'E3': 'EFL League Two',
                           'EC': 'National League',
                           'F1': 'France Ligue 1',
                           'F2': 'France Ligue 2',
                           'G1': 'Greece Super League',
                           'I1': 'Italy Serie A',
                           'I2': 'Italy Serie B',
                           'N1': 'Netherlands Eredivisie',
                           'P1': 'Liga Portugal',
                           'SC0': 'Scottish Premiership',
                           'SC1': 'Scottish Championship',
                           'SC2': 'Scottish League One',
                           'SC3': 'Scottish League Two',
                           'SP1': 'Primera Division',
                           'SP2': 'Segunda Division',
                           'T1': 'Turkey Süper Lig'}

other_leagues_dictionary = {'ARG': 'Argentina',
                            'AUT': 'Austria',
                            'BEL': 'Belgium',
                            'BRA': 'Brazil',
                            'CHN': 'China',
                            'DNK': 'Denmark',
                            'FIN': 'Finland',
                            'IRL': 'Ireland',
                            'JPN': 'Japan',
                            'MEX': 'Mexico',
                            'NOR': 'Norway',
                            'POL': 'Poland',
                            'ROU': 'Romania',
                            'RUS': 'Russia',
                            'SCO': 'Scotland',
                            'SWE': 'Sweden',
                            'SWZ': 'Switzerland',
                            'USA': 'USA'}


###############################################################################################################################

"""
These vars are used for scraping functions - Bookmakers' odds
"""

# Odds portal website CSS classes
CSS_SELECTOR_BUTTON = '#onetrust-accept-btn-handler'
CSS_SELECTOR_MATCHES = "div.eventRow"
CSS_SELECTOR_DATE_MATCH = '.text-black-main.font-main.w-full.truncate.text-xs.font-normal.leading-5'
CSS_SELECTOR_MATCH_DETAILS = 'div[class="border-black-borders border-b border-l border-r hover:bg-[#f9e9cc]"]'
CSS_SELECTOR_MATCH_TEAMS = 'p[class="participant-name truncate"]'
CSS_SELECTOR_MATCH_ODDS = 'div[class^="flex-center border-black-main min-w-"] p'


odds_base_url = "https://www.oddsportal.com/football/"

# Add the URL for the oddsportal championships url you want to get here
championship_url_dict = {'English Premier League' : 'england/premier-league/',
                         'France Ligue 1' : 'france/ligue-1/'}

# Web driver path (Firefox)
    # /!\ You need to have the geckodriver installed on your machine [Dockerfile.airflow already installs it]
driver_path = os.getenv("DRIVER_PATH", './geckodriver')



# Since team names can be different from one source to another, we need to update them
    # If you add a championship, you must compare team names between match histories files and odds files
update_team_names = {
    "Nottingham": "Nott'm Forest",
    "Manchester Utd": "Man United",
    "Manchester City": "Man City",
    "Sheffield Utd": "Sheffield United",
    "Paris SG": "PSG",
    "PSG": "Paris SG"}




###############################################################################################################################

"""
These vars are used for archiving functions
"""


# There's nothing here



###############################################################################################################################

"""
These vars are used for pre-processing functions
"""
columns_to_keep_for_features = ["Date",
                                "HomeTeam",
                                "AwayTeam",
                                "FTHG",
                                "FTAG",
                                "FTR",
                                "HTHG",
                                "HTAG", 
                                "HTR",
                                "HS",
                                "AS",
                                "HST",
                                "AST",
                                "HF",
                                "AF",
                                "HC",
                                "AC",
                                "HY",
                                "AY",
                                "HR",
                                "AR"]


###############################################################################################################################

"""
These vars are used for model training & evaluation functions
"""

# You can change parameters research, model, etc.
    # Be careful, the more parameters you have, the longer it will take to train the model
from sklearn.model_selection import GridSearchCV

model_params = {"C": [0.1, 1, 10, 100],
                "gamma": ["scale", "auto"],
                "kernel": ["linear", "rbf", "poly"],
                "probability": [True]}

from sklearn.svm import SVC
model= SVC()
grid = GridSearchCV(SVC(), model_params, cv=3, n_jobs=-1)


###############################################################################################################################

"""
These var are used for prediction functions
"""
# Kelly criterion multiplier
risk_aversion_coefficients = {"low": 0.5, "medium": 1.0, "high": 1.5}