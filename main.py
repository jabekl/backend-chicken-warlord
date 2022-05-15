import os
import secrets
from hashlib import sha256

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from db_func import database

load_dotenv("./.env")

app = FastAPI()
security = HTTPBasic()
db = database()

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

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "chickenWarlordAPI")
    correct_password = secrets.compare_digest(sha256(credentials.password.encode('ascii')).hexdigest(), os.getenv("hash"))

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/")
async def root(username: str = Depends(get_current_username)):
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
async def get_score(request: Request, username: str = Depends(get_current_username)):
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


@app.delete("/top-3-delete-entries-from-database")
async def delete_score(request: Request, username: str = Depends(get_current_username)):
    data = await request.json()
    return data