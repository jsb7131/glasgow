import json

from fastapi import Header, HTTPException

from utils.auth_utils import verify_password

USERS_FILE = "data/users.json"

def validate_user(username: str = Header(...), password: str = Header(...)):
    try:
        with open(USERS_FILE, "r") as f:
            users = json.load(f)
        for u in users.values():
            if u["username"] == username and verify_password(password, u["password"]):
                return u
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating user: {str(e)}")
    
    raise HTTPException(status_code=401, detail="Invalid credentials")
