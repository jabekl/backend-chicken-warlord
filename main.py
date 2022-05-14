from fastapi import FastAPI, Request
from db_func import database
from pydantic import BaseModel

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

@app.post("/top-3-post/")
async def get_score(request: Request):
    """
    Formatierung zur Punkteübergabe:

    {
    "name": "xy",
    "points": 0
    }      

    """
    data = await request.json()
    db.add_score(u_name=data['name'], u_score=data['points'])
    return data