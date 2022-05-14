from fastapi import FastAPI
from db_func import database
import json

app = FastAPI()

db = database()

@app.get("/")
async def root():
    top3 = db.get_top3()
    return [
        {
            "name": top3[0][0],
            "points": top3[0][1]
        },
        {
            "name": top3[1][0],
            "points": top3[1][1]
        },
        {
            "name": top3[2][0],
            "points": top3[2][1]
        }
    ]


# /top-3
# /top-3-post