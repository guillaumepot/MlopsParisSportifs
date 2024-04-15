
import sys
sys.path.insert(0, '.')
sys.path.insert(0, '../data_ml_functions')
sys.path.append("/src/data_ml_functions/")


from fastapi.testclient import TestClient
import pytest
import pandas as pd
from main import app



client = TestClient(app)


"""
Routes - Home
"""
# Test - /status route
def test_get_status():
    # With valid version
    response = client.get("/status", headers={"api-version": "1"})
    assert response.status_code == 200

    # With invalid version
    response = client.get("/status", headers={"api-version": "888"})
    assert response.status_code == 400
    print(response.content)

# Test - /available_championships route
def test_get_available_championships():
    # With valid version
    response = client.get("/available_championships", headers={"api-version": "1"})
    assert response.status_code == 200
    data = response.json()
    assert "Current Season" in data
    assert "Available Championships" in data
    assert "Available Teams" in data

    # With invalid version
    response = client.get("/available_championships", headers={"api-version": "888"})
    assert response.status_code == 400


"""
Routes - Authentification
"""
# Test - /signup route
def test_signup():
    # Create a new user
    user = {
        "username": "testuser",
        "password": "StrongPassword-123",
        "bankroll": 100,
        "risk": "low"
    }

    # Send a POST request to the /signup route
    response = client.post("/signup", json=user)

    # Check that the status code is 200
    assert response.status_code == 200
    # Check that the response message is "User created successfully"
    assert response.json() == {"message": "User created successfully"}

    # Try to create the same user again
    response = client.post("/signup", json=user)
    # Check that the status code is 500
    assert response.status_code == 500


# Test - /login route
@pytest.fixture                             # This fixture is used for an authentification token (free user)
def test_login_free():
    # User credentials
    form_data = {
        "username": "testuser",
        "password": "StrongPassword-123"
    }

    # Send a POST request to the /login route
    response = client.post("/login", data=form_data)

    # Check that the status code is 200
    assert response.status_code == 200

    # Check that the access token and token type are in the response
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    return data["access_token"]
   
@pytest.fixture                            # This fixture is used for an authentification token (premium & admin user)
def test_login_premium():
    # User credentials
    form_data = {
        "username": "admin",
        "password": "4dm1N-01"
    }

    # Send a POST request to the /login route
    response = client.post("/login", data=form_data)

    # Check that the status code is 200
    assert response.status_code == 200

    # Check that the access token and token type are in the response
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    return data["access_token"]



"""
Routes - User
"""
# Test - /user_info route
def test_user_info(test_login_free):
    # Access token
    headers = {
        "Authorization": f"Bearer {test_login_free}",
        "api-version": "1"
    }
    print(f"Headers: {headers}")

    # Send a GET request to the /user_info route
    response = client.get("/user_info", headers=headers)

    # Check that the status code is 200
    assert response.status_code == 200

    # Check that the user information is in the response
    data = response.json()
    assert "username" in data
    assert "bankroll" in data
    assert "risk" in data


# Test - /championship/{championship:str}/calendar route
@pytest.mark.parametrize("token, status_code", [                    # Test will use either the free or premium user token
    ("test_login_free", 402),
    ("test_login_premium", 200)])
def test_championship_calendar(request, token, status_code):
    token = request.getfixturevalue(token)

    # Access token
    headers = {
        "Authorization": f"Bearer {token}",
        "api-version": "1"
    }

    # Championship
    championship = "English Premier League"

    # Send a POST request to the /championship/{championship:str}/calendar route
    response = client.post(f"/championship/{championship}/calendar", headers=headers)

    # Check that the status code is as expected
    assert response.status_code == status_code

    if status_code == 200:
        # Check that the calendar data is in the response
        data = response.json()
        assert "message" not in data  # There should be no "message" key in the response if the request was successful
        assert isinstance(data, list)  # The response should be a list of dictionaries
        for match in data:
            assert "bet_advise" in match  # Each match should have a "bet_advise" key


# Test - /predict route
def test_predict(test_login_free):
    # Access token
    headers = {
        "Authorization": f"Bearer {test_login_free}",
        "api-version": "1"
    }

    championship = "English Premier League"
    matchs = pd.read_csv(f"../../storage/data/clean/{championship}/odds.csv")
    Home = matchs["HomeTeam"].iloc[0]
    Away = matchs["AwayTeam"].iloc[0]

    # Teams
    teams = {
        "championship": championship,
        "home_team": Home,
        "away_team": Away
    }

    # Send a POST request to the /predict route
    response = client.post("/predict", headers=headers, json=teams)

    # Check that the status code is 200
    assert response.status_code == 200

    # Check that the predictions are in the response
    data = response.json()
    assert isinstance(data, list)  # The response should be a list of dictionaries
    for prediction in data:
        assert "Date" in prediction
        assert "HomeTeam" in prediction
        assert "AwayTeam" in prediction
        assert "pred_home" in prediction
        assert "pred_draw" in prediction
        assert "pred_away" in prediction


# Test - /change/bankroll route
def test_change_bankroll(test_login_free):
    # Access token
    headers = {
        "Authorization": f"Bearer {test_login_free}",
        "api-version": "1"
    }

    # New bankroll
    new_bankroll = 500.0

    # Send a POST request to the /change/bankroll route
    response = client.post(f"/change/bankroll?new_bankroll={new_bankroll}", headers=headers)

    # Check that the status code is 200
    assert response.status_code == 200

    # Check that the response message is "Bankroll changed successfully"
    assert response.json() == {"message": "Bankroll changed successfully"}

    # Check that the bankroll has been updated
    response = client.get("/user_info", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "bankroll" in data
    assert data["bankroll"] == new_bankroll


# Test - /change/risk route
def test_change_risk(test_login_free):
    # Access token
    headers = {
        "Authorization": f"Bearer {test_login_free}",
        "api-version": "1"
    }

    # New risk level
    new_risk = "high"

    # Send a POST request to the /change/risk route
    response = client.post(f"/change/risk?new_risk={new_risk}", headers=headers)

    # Check that the status code is 200
    assert response.status_code == 200

    # Check that the response message is "Risk level changed successfully"
    assert response.json() == {"message": "Risk level changed successfully"}

    # Check that the risk level has been updated
    response = client.get("/user_info", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "risk" in data
    assert data["risk"] == new_risk


# Test - /change/password route
def test_change_password(test_login_free):
    # Access token
    headers = {
        "Authorization": f"Bearer {test_login_free}",
        "api-version": "1"
    }

    # Current and new password
    current_password = "StrongPassword-123"
    new_password = "NewStrongPassword-456"

    # Send a POST request to the /change/password route
    response = client.post(f"/change/password?current_password={current_password}&new_password={new_password}", headers=headers)

    # Check that the status code is 200
    assert response.status_code == 200

    # Check that the response message is "Password changed successfully"
    assert response.json() == {"message": "Password changed successfully"}

    # Try to login with the old password
    form_data = {
        "username": "testuser",
        "password": current_password
    }
    response = client.post("/login", data=form_data)
    # Check that the status code is 500
    assert response.status_code == 500

    # Try to login with the new password
    form_data = {
        "username": "testuser",
        "password": new_password
    }
    response = client.post("/login", data=form_data)
    # Check that the status code is 200
    assert response.status_code == 200



"""
Routes - Admin
"""
# Test - /admin/change/user route
def test_change_user(test_login_premium):
    # Access token
    headers = {
    "Authorization": f"Bearer {test_login_premium}",
    "api-version": "1"
    }
    
    user_to_change = 'testuser'
    new_user_data = {
        "new_username": "new_testuser",
        "new_bankroll": 10,
        "new_risk": "low",
        "new_role": "0"
    }
    response = client.put(f"/admin/change/{user_to_change}", headers=headers, json=new_user_data)
    assert response.status_code == 200
    assert response.json() == {"message": "User testuser datas changed."}



# Test - /admin/delete/user route
def test_delete_user(test_login_premium):
    # Access token
    headers = {
        "Authorization": f"Bearer {test_login_premium}",
        "api-version": "1"
    }

    # User to delete
    user_to_delete = "new_testuser"

    # Send a DELETE request to the /admin/delete/user route
    response = client.delete(f"/admin/delete/user/{user_to_delete}", headers=headers)

    # Check that the status code is 200
    assert response.status_code == 200

    # Check that the response message is "User {user_to_delete} deleted"
    assert response.json() == {"message": f"User {user_to_delete} deleted"}

    # Try to get the user info of the deleted user
    response = client.get(f"/user_info/{user_to_delete}", headers=headers)
    # Check that the status code is 404 (Not Found)
    assert response.status_code == 404