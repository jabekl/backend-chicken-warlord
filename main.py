from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "API für Chicken Warlord"}



# /top-3
# /top-3-post