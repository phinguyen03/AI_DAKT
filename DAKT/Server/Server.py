from fastapi import FastAPI, Query
import uvicorn
from pydantic import BaseModel
import pymongo
import numpy as np
import pandas as pd
from AI import load_and_prepare_data, RandomForest_Training, SVC_Training
import joblib

app = FastAPI()

myclient = pymongo.MongoClient("mongodb+srv://phi:123@cluster0.c3qpz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
mydb = myclient["Testmodel"]
mycol = mydb["mongotest"]


DATA_FILE = r'sensor_data.csv'

# Model
(X_train, X_test, y_train, y_test), scaler = load_and_prepare_data(DATA_FILE)
rdf = RandomForest_Training(X_train, X_test, y_train, y_test)[2]
svc = SVC_Training(X_train, X_test, y_train, y_test)[2]
scaler = joblib.load('preprocessor.pkl')

def inverse_mapping(val):
    if val == 0:
        return "Safe"
    elif val == 1:
        return "Signs of Water Pollution"
    else:
        return "Pollution"

class Item(BaseModel):
    pH: float
    Do_duc: float
    Nhiet_do: float
    thoi_gian: str
    khu_vuc: str
    kenh_song:str
    
    
@app.post("/update_post")
async def update_data_post(item: Item):
    input_df = pd.DataFrame([{
    "pH": item.pH,
    "Do duc (NTU)": item.Do_duc,
    "Nhiet do (°C)": item.Nhiet_do,
    "Khu vuc": item.khu_vuc,
    "Kenh": item.kenh_song
}])
    input_scaled = scaler.transform(input_df)
    prediction = int(svc.predict(input_scaled)[0])
    label = inverse_mapping(prediction)

    mydict = {
        "pH": item.pH,
        "Do_duc": item.Do_duc,
        "Nhiet_do": item.Nhiet_do,
        "thoi_gian": item.thoi_gian,
        "khu_vuc": item.khu_vuc,
        "kenh_song": item.kenh_song,
        "prediction": label
        
    }
    mycol.insert_one(mydict)
    return {"status": "success",
            "pH": mydict["pH"],
            "Do_duc": mydict["Do_duc"],
            "Nhiet_do": mydict["Nhiet_do"],
            "Thoi_gian": mydict["thoi_gian"],
            "Khu_vuc": mydict["khu_vuc"],
            "Kenh_song": mydict["kenh_song"],
            "prediction": label}

@app.get("/get")
async def get_data(limit: int = Query(1)):
    cursor = mycol.find().sort("thoi_gian", pymongo.DESCENDING).limit(limit)
    data_return = []
    
    for record in cursor:
        data_return.append({
            "pH": record['pH'],
            "Do_duc": record['Do_duc'],
            "Nhiet_do": record['Nhiet_do'],
            "thoi_gian": record['thoi_gian'],
            "khu_vuc": record["khu_vuc"],
            "kenh_song": record["kenh_song"],
            "prediction": record["prediction"]
        })

    return data_return

if __name__ == "__main__":
    uvicorn.run(app, host="192.168.1.5", port=8200)
