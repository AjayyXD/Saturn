import mysql.connector
from mysql.connector import Error
import os
import titan
import requests
from dotenv import load_dotenv

class db:

    def __init__(self):
        load_dotenv("variables.env")
        HOST = os.environ.get("DB_HOST")
        USER = os.environ.get("DB_USER")
        PASSWORD = os.environ.get("DB_PASSWORD")
        DATABASE = os.environ.get("DB_NAME")

        self.connection = mysql.connector.connect(
            host=HOST,
            user=USER,
            passwd=PASSWORD,
            database=DATABASE
        )
        self.cursor = self.connection.cursor(dictionary=True)
    def __enter__(self):
        return self
    def __exit__(self,exc_type,exc_val,exc_tb):
        if self.connection.is_connected():
            self.cursor.close()
            self.connection.close() 
    def setStats(self,id : int):
        try : 
            data = requests.get(f"http://127.0.0.1:8000/stats/{id}")
            data_dic = data.json()
            values = [
                (id, idx, int(v["avgTime"]), int(v["standardDeviation"]), int(v["count"]))
                for idx, v in data_dic.items()
            ]
            query = "REPLACE INTO ContestStats (ContestId,ProblemIndex,AvgTime,StandardDeviation,SolveCount) VALUES (%s,%s,%s,%s,%s);"
            if values :
                self.cursor.executemany(query,values)
                self.connection.commit()
                return data
        except Exception as e:
            print(e)
            
    def getContestStats(self,id : int):
        query = "SELECT ContestId,ProblemIndex,AvgTime,StandardDeviation,SolveCount FROM ContestStats WHERE ContestId = %s ORDER BY ProblemIndex ASC;"
        self.cursor.execute(query,(id,))
        data = self.cursor.fetchall()
        data_dic = {row['ProblemIndex']: row for row in data}
        if data:
            return data_dic
        else:
            return None
    def getQuestionStats(self,id : int, index : str):
        query = "SELECT ContestId,ProblemIndex,AvgTime,StandardDeviation,SolveCount FROM ContestStats WHERE ContestId = %s AND ProblemIndex = %s;"
        self.cursor.execute(query,(id,index))
        data = self.cursor.fetchall()
        if data:
            return data
        else:
            return None
    
    def idExists(self,id : int):
        query = "SELECT * FROM ContestStats WHERE ContestId = %s;"
        self.cursor.execute(query,(id,))
        data = self.cursor.fetchall()
        if data:
            return True
        return False
