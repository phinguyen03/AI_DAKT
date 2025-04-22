from time import sleep, strftime, time
from urllib import request
import numpy as np
import json


def Data(data1, data2, data3, data4, data5, data6):
  
    data = {
        "pH": data1,
        "Do_duc": data2,
        "Nhiet_do": data3,
        "thoi_gian": data4,
        "khu_vuc": data5,
        "kenh_song": data6
       
    }
    params = json.dumps(data).encode()
    return params


def MyPostJson(params):
    req = request.Request('http://192.168.1.5:8200/update_post', method="POST")
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
        req = request.Request('http://192.168.1.5:8200/get', method="GET")
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
    while True:
        pH = round(np.random.uniform(1, 13), 2)
        do_duc = round(np.random.uniform(0, 1000), 2)
        nhiet_do = round(np.random.uniform(0, 80), 2)
        thoi_gian = strftime('%Y-%m-%d %H:%M:%S')
        khu_vuc = "Go vap"
        kenh_song = "An Thong"

        sleep(2)
        count += 1
        params_json = Data(pH,
                           do_duc,
                           nhiet_do,
                           thoi_gian,
                           khu_vuc,
                           kenh_song)
        post_json = MyPostJson(params_json)
        print("Sending JSON data:", post_json)
        receive_data = my_get()
        print(receive_data)        

       
if __name__ == '__main__':
    main()