"""
Libraries
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

from datetime import datetime, timedelta
import os
import csv
import shutil
import re

from common_variables import CSS_SELECTOR_BUTTON, CSS_SELECTOR_MATCHES, CSS_SELECTOR_DATE_MATCH, CSS_SELECTOR_MATCH_DETAILS, CSS_SELECTOR_MATCH_TEAMS, CSS_SELECTOR_MATCH_ODDS
from common_variables import odds_base_url, championship_url_dict, driver_path, update_team_names, championships, path_data_source, path_data_raw





"""
Functions
"""
def initializeWebDriver(league_url: str):
    """
    Initializes and returns a WebDriver instance for scraping bookmakers' odds.

    Args:
        league_url (str): The URL of the league to scrape.

    Returns:
        WebDriver: The initialized WebDriver instance.

    """
    # Initialize options
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = '/usr/bin/firefox' 

    # Initialize the WebDriver
    os.environ['PATH'] += os.pathsep + '/opt/airflow/dags/'
    service = Service(driver_path)
    driver = webdriver.Firefox(service=service, options=options)

    # Get Website URL
    driver.get(league_url)

    return driver


def acceptCookies(driver):
    """
    Clicks on the cookies acceptance button.

    This function finds the cookies acceptance button on the webpage and clicks on it.
    If the button is not found, it prints an error message.

    Parameters:
    None

    Returns:
    None
    """
    try:
        cookies_accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, CSS_SELECTOR_BUTTON))
        )
        cookies_accept_button.click()
    except:
        print("Cookies button not found")


def ConvertOdds(odds):
    """
    Convert the odds from a fractional format to a decimal format.
    
    Args:
        cote (str): The odds in fractional format (e.g. "3/1").
        
    Returns:
        float: The converted odds in decimal format.
            If the conversion is not possible, the original odds are returned.
    """
    try:
        numerateur, denominateur = map(int, odds.split('/'))
        rapport = numerateur / denominateur
        return round(rapport, 2)  # Round to two decimal places for readability
    except ValueError:  # Handle cases where conversion is not possible
        return odds  # Return the original odds if they cannot be converted


def convertDate(date_str):
    """
    Converts a date string into a standardized format.

    Args:
        date_str (str): The date string to be converted.

    Returns:
        str: The converted date string in the format '%d/%m/%Y'.

    Raises:
        ValueError: If the input date string is not in a recognized format.

    """
    # Depending on the date, the date can be in different formats depending on the next match calendar

    if re.match(r'\d{2}/\d{2}/\d{4}', date_str):  # Check if date is in the format 'dd/mm/yyyy'
        date_object = datetime.strptime(date_str, '%d/%m/%Y')


    elif date_str.lower().startswith('tomorrow,'):
        date_str = date_str.split(',')[1].strip()
        date_object = datetime.strptime(date_str, '%d %b')
        date_object = date_object.replace(year=datetime.now().year)

    elif date_str.lower().startswith('today,'):
        date_str = date_str.split(',')[1].strip()
        date_object = datetime.strptime(date_str, '%d %b')
        date_object = date_object.replace(year=datetime.now().year)

    else:
        date_object = datetime.strptime(date_str, '%d %b %Y')

    return date_object.strftime('%d/%m/%Y')


def extract_match_info(match, last_date):
    """
    Extracts match information from a given match element.

    Args:
        match (WebElement): The match element containing the match details.
        last_date (str): The last date in case the date of the match is not found.

    Returns:
        dict: A dictionary containing the extracted match information with the following keys:
            - "Date": The date of the match.
            - "Home Team": The name of the home team.
            - "Away Team": The name of the away team.
            - "Odds 1": The odds for the home team.
            - "Odds X": The odds for a draw.
            - "Odds 2": The odds for the away team.
    """
    # Get the date
    try:
        date_match = match.find_element(By.CSS_SELECTOR, CSS_SELECTOR_DATE_MATCH).text
    except Exception:
        date_match = ""
        date_match = last_date

    date_match = convertDate(date_match)

    # Get the match details
    match_datas = match.find_elements(By.CSS_SELECTOR, CSS_SELECTOR_MATCH_DETAILS)

    for match_details in match_datas:
        # Teams
        teams = match_details.find_elements(By.CSS_SELECTOR, CSS_SELECTOR_MATCH_TEAMS)
        home_team = teams[0].text
        away_team = teams[1].text


        # Odds
        odd_datas = match_details.find_elements(By.CSS_SELECTOR, CSS_SELECTOR_MATCH_ODDS)
        
        if len(odd_datas) >= 3:
            odds_1 = odd_datas[0].text
            odds_x = odd_datas[1].text
            odds_2 = odd_datas[2].text
        else:
            print("Not enough odds data available for this match.")
            odds_1 = odds_x = odds_2 = 0  # Default value if odds are not available (kelly criterion need a value)


        odds_1 = ConvertOdds(odds_1) if odds_1 else odds_1
        odds_x = ConvertOdds(odds_x) if odds_x else odds_x
        odds_2 = ConvertOdds(odds_2) if odds_2 else odds_2
                

        # Create a dictionary with the match informations
        match_info = {
            "Date": date_match,
            "Home Team": home_team,
            "Away Team": away_team,
            "Odds 1": odds_1,
            "Odds X": odds_x,
            "Odds 2": odds_2}

    return match_info


def scrapOdds():
    """
    Scrapes bookmakers' odds for different championships.

    This function iterates over a list of championships and scrapes the bookmakers' odds for each championship.
    It initializes a WebDriver, accepts cookies, and extracts match details for each match in the championship.
    The match details are then saved to a CSV file.

    Args:
        None

    Returns:
        None
    """
    for championship in championships:
        # Define league URL
        league_url = odds_base_url + championship_url_dict[championship]

        # Initialize WebDriver
        driver = initializeWebDriver(league_url)

        # Wait before start scraping
        driver.implicitly_wait(5)

        # Accept cookies
        acceptCookies(driver)

        # Prepare match details extraction
        last_date = None
        all_match_details = []

        elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, CSS_SELECTOR_MATCHES)))

        # Find match elements
        matchs = driver.find_elements(By.CSS_SELECTOR, CSS_SELECTOR_MATCHES)

        # Extract match details
        for match in matchs:
            match_info = extract_match_info(match, last_date)

            # Update last date known value for matches
            if match_info['Date'] != last_date:
                last_date = match_info['Date']

            print(match_info)
            all_match_details.append(match_info)

        # Save all information to a CSV file
        # Create a file named 'odds.csv' in the directory
        destination_file = os.path.join(path_data_source, championship + '_odds.csv')

        with open(destination_file, 'w', newline='', encoding='utf-8') as fichier:
            writer = csv.writer(fichier)
            writer.writerow(['Date', 'HomeTeam', 'AwayTeam', 'Avg_H', 'Avg_D', 'Avg_A'])

            for match_details in all_match_details:
                home_team = match_details['Home Team']
                away_team = match_details['Away Team']

                # Update team names
                if home_team in update_team_names:
                    home_team = update_team_names[home_team]

                if away_team in update_team_names:
                    away_team = update_team_names[away_team]


                writer.writerow([match_details['Date'], home_team, away_team, match_details['Odds 1'], match_details['Odds X'], match_details['Odds 2']])


        shutil.copy(destination_file, path_data_raw + '/' + championship + '_odds.csv')
        driver.quit()  # Quit the WebDriver