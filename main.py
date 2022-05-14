from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from db_func import database

app = FastAPI()

origins = [
    "https://jabekl.github.io/chicken-warload/", 
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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