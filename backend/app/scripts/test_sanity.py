import requests
import uuid

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_auth():
    print("Running Auth Hackathon Check...")
    test_email = f"hack_{uuid.uuid4().hex[:6]}@example.com"
    password = "SuperSecretPassword123!"
    
    # 1. Register
    reg_res = requests.post(f"{BASE_URL}/auth/register", json={
        "email": test_email,
        "password": password,
        "display_name": "Hackathon User"
    })
    if reg_res.status_code == 200:
        print("PASS Registration")
    else:
        print(f"FAILED Registration: {reg_res.text}")
        return

    # 2. Login
    login_res = requests.post(f"{BASE_URL}/auth/login", json={
        "email": test_email,
        "password": password
    })
    
    if login_res.status_code == 200:
        token = login_res.json().get("data", {}).get("access_token")
        if token and token.startswith("hackathon_token_"):
            print("PASS Login and received valid hackathon token")
        else:
            print("FAILED Login token invalid")
    else:
        print(f"FAILED Login: {login_res.text}")

if __name__ == "__main__":
    test_auth()
