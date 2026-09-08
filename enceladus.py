from typing import Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import math
import time
import database
from fastapi.responses import JSONResponse


app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None

@app.get("/stats/{contestId}")
def getContestStats(contestId : int):
    with database.db() as db:
        data = db.getContestStats(contestId)
        if not data:
            raise HTTPException(status_code = 404,detail = "Contest not found")
        return data

@app.get("/stats/{contestId}/{index}")
def getQuestionStats(contestId : int,index : str):
    with database.db() as db:
        data = db.getQuestionStats(contestId,index)
        if not data:
            raise HTTPException(status_code = 404,detail="Contest not found")
        return data
    
@app.get("/stats/{contestId}/{index}/{user}")
def userSubmissionStats(contestId : int,index : str, user : str):
    try:
        found = 0
        data = requests.get(f"https://codeforces.com/api/user.status?handle={user}&from=1&count=100")
        data_dic = data.json()
        if data_dic["status"] != "OK":
            raise HTTPException(status_code = 404,detail = "Codeforces did not send any data. maybe wrong handle?")
        for submission in data_dic["result"] :
            valid = submission["problem"]["contestId"] == contestId and submission["problem"]["index"] == index and submission["verdict"] == "OK" and "c++" in submission["programmingLanguage"].lower()
            if valid :
                return submission["timeConsumedMillis"]
    except HTTPException as httpException:
        raise httpException
    except Exception as e:
        print(e)




    



