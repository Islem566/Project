from fastapi import FastAPI,Request,File,UploadFile,responses,HTTPException
import json
import datetime
from pymongo import MongoClient
from bson import ObjectId
from typing import List
from pydantic import BaseModel
import re
import uuid
from fastapi.responses import JSONResponse
import os
global content

# FastAPIinstance
app = FastAPI()
  
#connexion au mongodb 
client = MongoClient('mongodb://localhost:27017/')
db = client["test"]
mycollection = db["Catalogues"]
Transaction = db ["Transactions"]
#Route
 
class Transaction(BaseModel):
    transaction_id: str
    datetime: str


@app.post("/json/")
async def read_json(msisdn: int , canal: str , Option_Number: int,file: UploadFile = File(...)):  
    global content
    global now
    if msisdn is None:
        return JSONResponse(content={"error code": "1", "Error Message": "Not found"}, status_code=400)
   
    elif len(str(msisdn)) != 8 or not str(msisdn).isdigit(): 
        return JSONResponse(content={"error code" : "2", "ErrorMessage": "wrong format"}, status_code=400)
    
    if canal is None:
        return JSONResponse(content={"error code": "3", "Error Message": "Not found"}, status_code=400)
   
    elif canal not in ["ussd", "web"]:
        return JSONResponse(content={"Errorcode": "4" , "ErrorMessage": "Canal Not allowed" }, status_code=400)
    if Option_Number is None:
         return JSONResponse(content={"Errorcode": "4" , "ErrorMessage": "Canal Not allowed" }, status_code=400)
    
    elif Option_Number > 5:
        return JSONResponse(content={"error code" : "5" ,  "ErrorMessage":  "Number option must be < 5 "}, status_code=400)
    
    contents = await file.read()
    body = json.loads(contents)
    expiryDate = False
    ServiceCurrent= False
    for d in body:

     if "supervisionExpiryDate" in d and d["supervisionExpiryDate"] is not None:
        expiryDate = True

        if datetime.datetime.strptime(d['supervisionExpiryDate'][:-6], '%Y%m%dT%H:%M:%S') < datetime.datetime.today():

             return JSONResponse(content={"expiration date": d['supervisionExpiryDate'], "message": " msisdn expired"}, status_code=400)
     if not expiryDate:
         return JSONResponse(content={"ErrorMessage": "supervisionExpiryDate Not found"}, status_code=400)
      
     if "serviceClassCurrent" in d and d["serviceClassCurrent"] is not None:
        ServiceCurrent= True

    if not ServiceCurrent:
        return JSONResponse(content={"ErrorMessage": "serviceClassCurrent Not found"}, status_code=400)
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    now = datetime.datetime.now()
    service_class_current = body[0]["serviceClassCurrent"]
    result = ";" + service_class_current +";"
    cursor =db.Catalogues.find({"serviceClassEligible": re.compile(result)})
    
    mydict= [{"_id": timestamp , "option": "4GO" , "type": "voix" ,"code":"opp1" , "price": "3500" , "serviceClasseEligible": ";1;2;3;4;9;10;" 
             }]
    x = db.Catalogues.insert_One(mydict)
    
    
   
      
      
   
   
   
   

@app.post("/")
async def read(file: UploadFile = File(...)):
    
    contents = await file.read()
    
    data = json.loads(contents)
    account_dict = None
    for item in data:
      if "AccountValue" in item:
           account_dict = item
           break

# Check if a valid dictionary element was found
    if account_dict is None:
       raise ValueError("No dictionary element with 'AccountValue' key found in data")

# Retrieve options from the database based on the AccountValue
    res= db.Catalogues.find({"price": {"$lte": account_dict["AccountValue"]}})
        
    options = []
    for option in res:
        options.append(option)
    if not options:
        raise HTTPException(status_code=404, detail="Aucune option disponible")
    return options
   
    
  


 


@app.get("/status/{transaction_id}")
async def get_status(transaction_id: str):
  
    check= db.Transactions.update_one(
        {"transaction_id": transaction_id},
        {"$set": {"OptionsStatus": "Sucess"}},
        upsert=False
    )
    
    if check.modified_count > 0:
        db.Transactions.update_one(
            {"transaction_id": transaction_id},
            {"$set": {"OptionsStatus": "Not Sucess"}},
            upsert=False
        )
        return {"status": "sucess"}
    else:
        return {"status": " NOt Sucess"}
                                 
  

            
    














