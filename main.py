from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from db_func import database
import json
import uvicorn
import os

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

app.post("/top-3-post/")
async def get_score(data: Request):
    responseData = await data.json()
    return responseData

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
