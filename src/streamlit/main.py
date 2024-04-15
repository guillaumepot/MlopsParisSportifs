import streamlit as st
import requests
import os
import pandas as pd

api_version_header = {"api-version": "1"}

api_url = os.getenv("API_URL")
api_port = os.getenv("API_PORT")

api_base_url = f"{api_url}:{api_port}"

# Function to fetch available teams based on selected championship
def fetch_available_teams(championship):
    headers = {"accept": "application/json", "api-version": "1"}
    response = requests.get(f"{api_base_url}/available_championships", headers=headers)
    
    if response.status_code == 200:
        available_teams = response.json().get("Available Teams", {}).get(championship, [])
        return available_teams
    else:
        st.error("Failed to fetch available teams.")
        return []


# Initialize session state if not already done
if 'access_token' not in st.session_state:
    st.session_state.access_token = None

# Streamlit UI
st.set_page_config(
    page_title="Football Match Prediction",
    page_icon=":soccer:"
)
st.markdown("""
## Welcome to our Sports Betting Application!
""")
st.image("/app/streamlit/image_streamlit.png", use_column_width=True)

st.markdown("""
This application is designed to enhance users' chances of winning in sports betting, focusing specifically on various national soccer leagues across Europe.

### How It Works

The process for achieving this goal involves three successive steps:

1. **Create a Secure Account**: This includes providing a login, password, bankroll, and risk level. The "bankroll" represents the total amount of money the user is willing to allocate to betting activities.

2. **Log In**: Once the account is created, users can log in with their credentials.

3. **Predict Match Outcomes**: The application utilizes a machine learning model to estimate the probabilities of future match results.

### Additional Features

Depending on the user's role (standard or premium), additional information on the bet made is provided. Premium users are given the amount of the optimal bet, calculated according to Kelly's criterion - the share of the bankroll to be risked on this bet.

By default, the user's role is standard. To upgrade to a premium user, please contact us!

 
""")
st.markdown("---") 

# Authentication
st.sidebar.title("Authentication")
selected_option = st.sidebar.selectbox(
    "Choose an option",
    ["", "Sign Up", "Log In"],
)

if selected_option == "Sign Up":
    st.sidebar.subheader("Sign Up")
    signup_username = st.sidebar.text_input("Username")
    signup_password = st.sidebar.text_input("Password", type="password")
    signup_bankroll = st.sidebar.number_input("Bankroll")
    signup_risk = st.sidebar.selectbox("Risk Level", ["low", "medium", "high"])

    if st.sidebar.button("Sign Up"):
        signup_data = {
            "username": signup_username,
            "password": signup_password,
            "bankroll": signup_bankroll,
            "risk": signup_risk.lower()
        }
        response = requests.post(f"{api_base_url}/signup", headers=api_version_header, json=signup_data)
        if response.status_code == 200:
            st.sidebar.success("Sign Up Successful!")
        else:
            st.sidebar.error(response.json())

elif selected_option == "Log In":
    st.sidebar.subheader("Log In")
    login_username = st.sidebar.text_input("Username")
    login_password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Log In"):
        login_data = {
            "grant_type": "",
            "username": login_username,
            "password": login_password,
            "scope": "",
            "client_id": "",
            "client_secret": ""
        }
        url = f"{api_base_url}/login"
        headers = {"accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(url, headers=headers, data=login_data)
        if response.status_code == 200:
            st.sidebar.success("Logged In Successfully!")
            access_token = response.json().get("access_token")
            st.session_state.access_token = access_token
            
        else:
            st.sidebar.error("Incorrect Username or Password.")

# Logout button
if st.session_state.access_token:
    st.sidebar.empty()
    st.sidebar.button("Log Out", on_click=lambda: st.session_state.pop('access_token'))
    st.sidebar.empty()

# Modify account settings...
if selected_option:
    st.sidebar.title("Modify Account Settings")
    selected_option_account = st.sidebar.selectbox(
        "Modify Settings",
        ["", "Change Password", "Change Bankroll", "Change Risk Level", "Show My Data"]
    )

    if selected_option_account == "Change Password":
        st.sidebar.subheader("Change Password")
        access_token = st.session_state.access_token
        if access_token:
            current_password = st.sidebar.text_input("Current Password", type="password", key="current_password")
            new_password = st.sidebar.text_input("New Password", type="password", key="new_password")
            save_password_button = st.sidebar.button("Save Password", key="save_password_button")
            
            if save_password_button:
                url = f"{api_base_url}/change/password?current_password={current_password}&new_password={new_password}"
                headers = {
                    "accept": "application/json",
                    "api-version": "1",
                    "Authorization": f"Bearer {access_token}"
                }
                response = requests.post(url, headers=headers)
                if response.status_code == 200:
                    st.sidebar.success("Password Changed Successfully!")
                else:
                    st.sidebar.error(response.json())
        else:
            st.sidebar.error("Please Log In to change your password.")

    elif selected_option_account == "Change Bankroll":
        st.sidebar.subheader("Change Bankroll")
        access_token = st.session_state.access_token
        if access_token:
            new_bankroll = st.sidebar.number_input("New Bankroll", key="new_bankroll")
            save_bankroll_button = st.sidebar.button("Save Bankroll", key="save_bankroll_button")
            
            if save_bankroll_button:
                url = f"{api_base_url}/change/bankroll?new_bankroll={new_bankroll}"
                headers = {
                    "accept": "application/json",
                    "api-version": "1",
                    "Authorization": f"Bearer {access_token}"
                }
                response = requests.post(url, headers=headers)
                if response.status_code == 200:
                    st.sidebar.success("Bankroll Changed Successfully!")
                else:
                    st.sidebar.error(response.json())
        else:
            st.sidebar.error("Please Log In to change your bankroll.")

    elif selected_option_account == "Change Risk Level":
        st.sidebar.subheader("Change Risk Level")
        access_token = st.session_state.access_token
        if access_token:
            new_risk = st.sidebar.selectbox("New Risk Level", ["low", "medium", "high"], key="new_risk")
            save_risk_button = st.sidebar.button("Save Risk Level", key="save_risk_button")
            
            if save_risk_button:
                url = f"{api_base_url}/change/risk?new_risk={new_risk}"
                headers = {
                    "accept": "application/json",
                    "api-version": "1",
                    "Authorization": f"Bearer {access_token}"
                }
                response = requests.post(url, headers=headers)
                if response.status_code == 200:
                    st.sidebar.success("Risk Level Changed Successfully!")
                else:
                    st.sidebar.error(response.json())
        else:
            st.sidebar.error("Please Log In to change your risk level.")

    elif selected_option_account == "Show My Data":
        st.sidebar.subheader("My Information")
        access_token = st.session_state.access_token
        if access_token:
            headers = {
                "accept": "application/json",
                "api-version": "1",
                "Authorization": f"Bearer {access_token}"
            }
            response = requests.get(f"{api_base_url}/user_info", headers=headers)
            if response.status_code == 200:
                user_info = response.json()
                st.sidebar.write("User Data:")
                st.sidebar.write(user_info)
            else:
                st.sidebar.error("Error retrieving user data.")
        else:
            st.sidebar.error("Please Log In to view your data.")

# Administrator Actions
if st.session_state.access_token:
    access_token = st.session_state.access_token
    headers = {
        "accept": "application/json",
        "api-version": "1",
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(f"{api_base_url}/user_info", headers=headers)
    if response.status_code == 200:
        user_info = response.json()
        if user_info.get("role") == 9:  # If user is administrator
            st.sidebar.title("Administrator Actions")
            selected_option_admin = st.sidebar.selectbox(
                "Select an Action",
                ["", "Delete User", "Modify User"]
            )

            if selected_option_admin == "Delete User":
                st.sidebar.subheader("Delete User")
                username_to_delete = st.sidebar.text_input("Username to Delete", key="username_to_delete")
                delete_user_button = st.sidebar.button("Delete User")

                if delete_user_button:
                    url = f"{api_base_url}/admin/delete/user/{username_to_delete}"
                    response = requests.delete(url, headers=headers)
                    if response.status_code == 200:
                        st.sidebar.success("User Deleted Successfully!")
                    else:
                        st.sidebar.error(response.json())

            elif selected_option_admin == "Modify User":
                st.sidebar.subheader("Modify User")
                username_to_modify = st.sidebar.text_input("Username to Modify", key="username_to_modify")
                new_username = st.sidebar.text_input("New Username", key="new_username")
                new_bankroll = st.sidebar.number_input("New Bankroll", key="new_bankroll_admin")
                new_risk = st.sidebar.selectbox("New Risk Level", ["low", "medium", "high"], key="new_risk_admin")
                new_role = st.sidebar.selectbox("New Role", [0, 1, 9], key="new_role_admin")
                modify_user_button = st.sidebar.button("Modify User")

                if modify_user_button:
                    modify_data = {
                        "new_username": new_username,
                        "new_bankroll": new_bankroll,
                        "new_risk": new_risk,
                        "new_role": new_role
                    }
                    url = f"{api_base_url}/admin/change/{username_to_modify}"
                    response = requests.put(url, headers=headers, json=modify_data)
                    if response.status_code == 200:
                        st.sidebar.success("User Modified Successfully!")
                    else:
                        st.sidebar.error(response.json())

# Predict upcoming matches (premium user)
if st.session_state.access_token :
    if user_info.get("role") == 1 or user_info.get("role") == 9:
        st.subheader("Predict upcoming matches")
        with st.container(border=True):
            selected_championship = st.selectbox("Championship", ["English Premier League", "France Ligue 1"], key="championship_premium_user")
            if st.button("View predicted results of upcoming matches"):
                access_token = st.session_state.access_token
                if access_token:
                    headers = {
                        "accept": "application/json",
                        "api-version": "1",
                        "Authorization": f"Bearer {access_token}"
                    }
                    response = requests.post(f"{api_base_url}/championship/{selected_championship}/calendar", headers=headers)
                    if response.status_code == 200:
                        match_calendar = response.json()
                        st.write("Upcoming matches:")
                        df = pd.DataFrame(match_calendar)
                        # Apply conditional styling
                        def highlight_max_row(s):
                            is_max = s == s.max()
                            return ['background-color: yellow' if v else '' for v in is_max]

                        # Apply row-wise conditional styling
                        df_styled = df.style.apply(highlight_max_row, subset=["pred_home", "pred_draw", "pred_away"], axis=1)

                        st.dataframe(df_styled)  
                        st.info("Interpretation of bet_advise values: When the value is negative, it's recommended not to bet on the match, as the risk of loss outweighs the potential gain.", icon="ℹ️")
                    else:
                        st.error("Failed to retrieve upcoming matches.")
                else:
                    st.error("Please log in to view upcoming matches.")


# Match prediction (standard user)
if st.session_state.access_token:
    if user_info.get("role") == 0 or user_info.get("role") == 9:
        st.subheader("Match Prediction")
        with st.container(border=True):
            st.warning("Please note that only upcoming matches can be selected for prediction.")
            championship = st.selectbox("Championship", ["English Premier League", "France Ligue 1"], key="championship_standard_user")
            
            # Fetch available teams dynamically based on selected championship
            available_teams = fetch_available_teams(championship)
            
            # Display dropdowns for home and away teams
            home_team = st.selectbox("Home Team", available_teams, key="home_team_standard_user")
            away_team = st.selectbox("Away Team", available_teams, key="away_team_standard_user")

            if st.button("Predict match result"):
                access_token = st.session_state.access_token
                if access_token:
                    predict_data = {
                        "home_team": home_team,
                        "away_team": away_team,
                        "championship": championship
                    }
                    headers = {
                        "accept": "application/json",
                        "api-version": "1",
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    }
                    response = requests.post(f"{api_base_url}/predict", headers=headers, json=predict_data)
                   
                    if response.status_code == 200:
                        st.write("Prediction result:")
                        prediction_result = response.json()

                        for prediction in prediction_result:
                            st.write("-----------------------------")
                            st.write(f"Date: {prediction['Date']}")
                            st.write(f"Home Team: {prediction['HomeTeam']}")
                            st.write(f"Away Team: {prediction['AwayTeam']}")
                            st.write(f"Predicted Home Win Probability: {prediction['pred_home'] * 100:.0f}%")
                            st.write(f"Predicted Draw Probability: {prediction['pred_draw'] * 100:.0f}%")
                            st.write(f"Predicted Away Win Probability: {prediction['pred_away'] * 100:.0f}%")
                    else:
                        st.error("Failed to retrieve prediction.")
                else:
                    st.error("Please log in to make a prediction.")
        # Encourage the user to upgrade to premium for more betting advice
        st.info("Upgrade to premium for more betting advice and predictions! Contact us to change your role.", icon="ℹ️")