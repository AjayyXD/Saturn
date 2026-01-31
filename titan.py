from typing import Union
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import requests
import math
import time
import logging


app = FastAPI()

saturn_logger = logging.getLogger("saturn_api")
saturn_logger.setLevel(logging.ERROR)
fh = logging.FileHandler('saturn_errors.log')
formatter = logging.Formatter('%(asctime)s | %(message)s')
fh.setFormatter(formatter)
saturn_logger.addHandler(fh)
saturn_logger.propagate = False

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None

def getIndices(constestId : int):
    data = requests.get(f"https://codeforces.com/api/contest.standings?contestId={constestId}&from=1&count=1&showUnofficial=true",timeout=25)
    time.sleep(1)
    dataDic = data.json()
    indices = []
    for result in dataDic["result"]["problems"]:
        indices.append(result["index"])
    return indices





@app.get("/stats/{contestId}")
def contestStats(contestId : int):
    indices = getIndices(contestId)
    stats = {}
    offset = 1
    count = {index : 0 for index in indices}
    totalTime = {index : 0 for index in indices}
    totalSquaredTime = {index : 0 for index in indices}
    avgTime = {index : 0 for index in indices}
    standardDeviation = {index : 0 for index in indices}
    dataFilled = False
    while(not dataFilled and offset < 200000):
        try : 
            data = requests.get(f"https://codeforces.com/api/contest.status?contestId={contestId}&from={offset}&count={5000}",timeout=25)
            dataDic = data.json()
            if not (dataDic["status"] == "OK"):
                raise HTTPException(status_code=500,detail = "Codeforces did not send any data")
            for submission in dataDic["result"]:
                lang = submission["programmingLanguage"].lower()
                isCpp = "c++" in lang
                if isCpp and submission["verdict"] == "OK":
                    count[submission["problem"]["index"]] = count[submission["problem"]["index"]] + 1
                    totalTime[submission["problem"]["index"]] = totalTime[submission["problem"]["index"]] + submission["timeConsumedMillis"]
                    totalSquaredTime[submission["problem"]["index"]] = totalSquaredTime[submission["problem"]["index"]] + submission["timeConsumedMillis"]**2
                print(f"offset:{offset},index:{submission["problem"]["index"]},count:{count[submission["problem"]["index"]]}")
            notFound = True
            for index in indices:   
                if count[index]<50:
                    notFound = False
                    break
            if notFound:
                dataFilled = True
            time.sleep(1)
        except HTTPException as http_exception : 
            saturn_logger.error(f"CONTEST: {contestId} | FAILED | Error: {str(http_exception)}")
        except Exception as e:
            saturn_logger.error(f"CONTEST: {contestId} | FAILED | Error: {str(e)}")
        finally : 
            offset = offset + 5000
    try :
        for index in indices : 
            if count[index] == 0:
                continue
            avgTime[index] = totalTime[index]/count[index]
            variance = (totalSquaredTime[index]/count[index]) - avgTime[index]**2
            standardDeviation[index] = max(0, variance)**0.5
            stats[index] = {
                "avgTime" : round(avgTime[index],2),
                "standardDeviation" : round(standardDeviation[index],2),
                "count" : count[index]
            }
        return stats
    except Exception as e:
        saturn_logger.error(f"CONTEST: {contestId} | FAILED | Error: {str(e)}")
        return None

        
@app.get("/stats/contest={contestId}?index={index}")
def questionStats(contestId : int, index:str):
    offset = 1
    count = 0
    totalTime = 0
    totalSquaredTime = 0
      
    while(count<50):
        try :            
            data = requests.get(f"https://codeforces.com/api/contest.status?contestId={contestId}&from={offset}&count={5000}",timeout=25)
            data_dic = data.json()
            offset = offset+5000
            for submission in data_dic["result"]:
                lang = submission["programmingLanguage"].lower()
                isCpp = "c++" in lang
                if submission["problem"]["index"] == index and isCpp and submission["verdict"] == "OK":
                    count = count + 1
                    totalTime = totalTime + submission["timeConsumedMillis"]
                    totalSquaredTime = totalSquaredTime + submission["timeConsumedMillis"]**2
            print(f"offset:{offset},count:{count}")
            time.sleep(1)
        except Exception as e:
            return e
    avgTime = math.ceil(totalTime/count)
    standardDeviation = math.ceil(max((totalSquaredTime/count - (avgTime)**2),0)**0.5)
    print(f"total count:{count}")
    print(f"Avg time : {avgTime}ms")
    print(f"Standard deviation : {standardDeviation}")
    stats = {
        "avgTime" : avgTime,
        "standardDeviation" : standardDeviation,
        "count" : count
    }

        
    return stats

