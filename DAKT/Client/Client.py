from time import sleep, strftime, time
from urllib import request
import numpy as np
import json


def Data(data1, data2, data3):
  
    data = {
        "pH": data1,
        "Do_duc": data2,
        "Nhiet_do": data3,
       
    }
    params = json.dumps(data).encode()
    return params


def MyPostJson(params):
    req = request.Request('http://192.168.1.10:8002/update_post', method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("accept", "application/json")
    
    try:
        r = request.urlopen(req, data=params)
        response_data = r.read()
        return response_data
    except Exception as e:
        print(f"Error posting JSON data: {e}")
        return None

def my_get():
    try:
        req = request.Request('http://192.168.1.10:8001/get', method="GET")
        req.add_header("accept", "application/json")  
        r = request.urlopen(req)
        response_data = r.read().decode()
        response_json = json.loads(response_data)  # Convert json to dict type
        return response_json
    except Exception as e:
        print(f"Error getting data: {e}")
        return None
    
def main():
    count = 0   
    timenow = strftime('%Y-%m-%d %H:%M:%S')
    while True:
        pH = np.random.uniform(1, 13)
        do_duc = np.random.uniform(0, 1000)
        nhiet_do = np.random.uniform(0, 80)

        sleep(2)
        count += 1
        params_json = Data(pH, do_duc, nhiet_do)
        post_json = MyPostJson(params_json)
        print("Sending JSON data:", post_json)
        #receive_data = my_get()
        #print(receive_data)        

       
if __name__ == '__main__':
    main()