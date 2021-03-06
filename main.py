import os
import secrets
from hashlib import sha256

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from db_func import database
from Middleware import CheckHost, HTTPSRedirect, GZipHandler, RateLimiting

load_dotenv("./.env")


security = HTTPBasic()
db = database()

origins = [
    "*"
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'DELETE'],
    allow_headers=["*"],
)
app.add_middleware(HTTPSRedirect) #comment out while testing in local network
app.add_middleware(CheckHost)
app.add_middleware(GZipHandler, minimum_size=1000)
app.add_middleware(RateLimiting)

def user(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "chickenWarlordAPI")
    correct_password = secrets.compare_digest(sha256(credentials.password.encode('ascii')).hexdigest(), os.getenv("hash"))

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials

@app.get("/")
@app.get("")
async def root(user: str = Depends(user)) -> list:
    top3 = db.get_top3()

    res = [

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
    return res


@app.post("/top-3-post/")
@app.post("/top-3-post")
async def get_score(request: Request, user: str = Depends(user)) -> dict:
    """
    Formatierung zur Datenübergabe:

    {
    "name": "xy",
    "points": 0
    }      

    """
    data = await request.json()
    result = db.add_score(u_name=data['name'], u_score=data['points'])


    res = {
        "status": result[0],
        "recieved": data
    }
    return res

@app.delete("/top-3-delete/")
@app.delete("/top-3-delete")
async def delete(request: Request, user: str = Depends(user)) -> dict:
    """
    Formatierung zur Datenübergabe:
    
    { "name": "xy" }
    """
    data = await request.json()
    name = data['name']

    result = db.delete(name)


    res =  {"status": result[0]}
    return res
