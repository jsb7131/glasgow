import json
import pandas as pd

USERS_FILE = "data/users.json"
SORT_BOTS_FILE = "data/sort_bots.json"

def generate_leaderboard(board: str = "small", sort: str = "asc"):
    with open(USERS_FILE) as f1, open(SORT_BOTS_FILE) as f2:
        users = json.load(f1)
        bots = json.load(f2)

    if not bots:
        return []

    df_users = pd.DataFrame.from_dict(users, orient="index")
    df_bots = pd.DataFrame.from_dict(bots, orient="index")

    runtime_column = f"avg_{board}_input_runtime"
    if runtime_column not in df_bots.columns:
        return []

    df_bots[runtime_column] = df_bots[runtime_column].astype(float)
    merged = df_bots.merge(df_users, on="user_id")
    merged = merged.sort_values(by=runtime_column, ascending=(sort == "asc"))

    leaderboard = []
    for idx, row in enumerate(merged.itertuples(), 1):
        rank = idx if sort == "asc" else len(merged) - idx + 1
        leaderboard.append({
            "position": rank,
            "username": row.username,
            "bot_name": row.bot_name,
            "bot_description": row.bot_description,
            "runtime": getattr(row, runtime_column)
        })
    return leaderboard
