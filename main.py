from fastapi import FastAPI
from routes import auth, sort_bot

app = FastAPI(
    title="Sort Bot API",
    description="Submit sorting code to compete on the benchmarking leaderboard"
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(sort_bot.router, prefix="/api/v1")
