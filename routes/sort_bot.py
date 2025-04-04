import uuid
import json
import os
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from routes.base.security import validate_user
from utils.code_runner import validate_code, sanitize_runtime, run_code
from utils.leaderboard import generate_leaderboard

router = APIRouter()

SORT_BOTS_FILE = "data/sort_bots.json"

class SortBotSubmission(BaseModel):
    code: str = Field(..., min_length=1)

class BoardType(str, Enum):
    small = "small"
    medium = "medium"
    large = "large"

class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"

@router.post("/submit-and-run-bot")
def submit_bot(
    submission: SortBotSubmission,
    user=Depends(validate_user),
    bot_name: str = Header(...),
    bot_description: str = Header(...),
):
    try:
        validated = validate_code(submission.code)
        if not validated:
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid or unsafe code"}
            )

        if not os.path.exists(SORT_BOTS_FILE):
            with open(SORT_BOTS_FILE, "w") as f:
                json.dump({}, f)

        with open(SORT_BOTS_FILE, "r") as f:
            try:
                bots = json.load(f)
            except json.JSONDecodeError:
                bots = {}

        # Check if user already has a bot with the same name
        for existing in bots.values():
            if existing["user_id"] == user["user_id"] and existing["bot_name"].lower() == bot_name.lower():
                return JSONResponse(
                    status_code=400,
                    content={"detail": "You already have a bot with that name."}
                )
            
        avg_small, avg_medium, avg_large = run_code(submission.code)
        
        bot_id = str(uuid.uuid4())
        bots[bot_id] = {
            "user_id": user["user_id"],
            "bot_name": bot_name,
            "bot_description": bot_description,
            "bot_code": submission.code,
            "avg_small_input_runtime": sanitize_runtime(avg_small),
            "avg_medium_input_runtime": sanitize_runtime(avg_medium),
            "avg_large_input_runtime": sanitize_runtime(avg_large)
        }

        with open(SORT_BOTS_FILE, "w") as f:
            json.dump(bots, f, indent=4)

        # return all leaderboards when submitting a new bot
        return {
            "small_input_leaderboard": generate_leaderboard("small", "asc"),
            "medium_input_leaderboard": generate_leaderboard("medium", "asc"),
            "large_input_leaderboard": generate_leaderboard("large", "asc")
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running and submitting bot: {str(e)}")
    

@router.get("/get-leaderboard")
def get_leaderboard(
    user=Depends(validate_user),
    board: BoardType = Query("small"),
    sort: SortOrder = Query("asc")
):
    try:
        board_value = board.value if isinstance(board, BoardType) else board
        sort_value = sort.value if isinstance(sort, SortOrder) else sort
        key_name = f"{board_value}_input_leaderboard"
        return {key_name: generate_leaderboard(board_value, sort_value)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating leaderboard: {str(e)}")
