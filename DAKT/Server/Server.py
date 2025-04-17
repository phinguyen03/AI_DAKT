from fastapi import FastAPI, Query
import uvicorn
from pydantic import BaseModel
import pymongo
from datetime import datetime
import numpy as np
from AI import load_and_prepare_data, RandomForest_Training, SVC_Training
import joblib

app = FastAPI()

myclient = pymongo.MongoClient("mongodb+srv://phi:123@cluster0.c3qpz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
mydb = myclient["Testmodel"]
mycol = mydb["mongotest"]


DATA_FILE = r'DATASET.csv'

# Model
X_train, X_test, y_train, y_test = load_and_prepare_data(DATA_FILE)
rdf = RandomForest_Training(X_train, X_test, y_train, y_test)[2]
svc = SVC_Training(X_train, X_test, y_train, y_test)[2]
scaler = joblib.load('scaler.pkl')

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
    thoi_gian: datetime
    khu_vuc: str
    kenh_song:str
    
    
@app.post("/update_post")
async def update_data_post(item: Item):
    input_data = np.array([[item.pH, item.Do_duc, item.Nhiet_do]])
    input_scaled = scaler.transform(input_data)
    prediction = int(rdf.predict(input_scaled)[0])
    label = inverse_mapping(prediction)

    mydict = {
        "pH": item.pH,
        "Do_duc": item.Do_duc,
        "Nhiet_do": item.Nhiet_do,
        "thoi_gian": datetime.now(),
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
async def get_data(limit: int = Query(10)):
    cursor = mycol.find().sort("time", pymongo.DESCENDING).limit(limit)
    data_return = []
    
    for record in cursor:
        data_return.append({
            "id": record['id'],
            "time": record['time'],
            "data1": record['data1'],
            "data2": record['data2'],
        })

    return data_return

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
