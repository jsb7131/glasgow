import uuid
import json
import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from utils.auth_utils import hash_password

router = APIRouter()

USERS_FILE = "data/users.json"

class SignupInput(BaseModel):
    username: str = Field(..., min_length=5)
    password: str = Field(..., min_length=6)

@router.post("/signup")
def signup(data: SignupInput):
    username = data.username
    password = data.password

    try:
        if not os.path.exists(USERS_FILE):
            with open(USERS_FILE, "w") as f:
                json.dump({}, f)
    
        with open(USERS_FILE, "r+") as f:
            try:
                users = json.load(f)
            except json.JSONDecodeError:
                users = {}

            for user in users.values():
                if user["username"] == username:
                    return JSONResponse(status_code=400, content={"detail": "User already exists"})

            user_id = str(uuid.uuid4())
            users[user_id] = {
                "user_id": user_id,
                "username": username,
                "password": hash_password(password)
            }

            f.seek(0)
            f.truncate()
            json.dump(users, f, indent=4)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not register user: {str(e)}")

    return {"message": "User successfully created"}
