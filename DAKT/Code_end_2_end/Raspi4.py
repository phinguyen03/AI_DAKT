from time import sleep, strftime
from urllib import request
import json
import board
import busio
import digitalio
import adafruit_rfm9x

# LoRa configuration
RADIO_FREQ_MHZ = 433.0
CS = digitalio.DigitalInOut(board.CE1)
RESET = digitalio.DigitalInOut(board.D25)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Cấu hình để tăng khoảng cách
rfm9x = adafruit_rfm9x.RFM9x(
    spi, CS, RESET, RADIO_FREQ_MHZ,
    baudrate=100000,
    tx_power=23,           # Công suất tối đa
    spreading_factor=9,    # SF9: Tăng khoảng cách
    signal_bandwidth=125000,  # BW 125 kHz
    coding_rate=8          # CR 4/8: Tăng độ bền tín hiệu
)

def validate_data(pH, do_duc, nhiet_do, khu_vuc, kenh_song):
    """Validate sensor data ranges and strings"""
    try:
        print(f"Validating: pH={pH}, Do_duc={do_duc}, Nhiet_do={nhiet_do}, khu_vuc={khu_vuc}, kenh_song={kenh_song}")
        pH = float(pH)  # Chuyển pH2 thành float
        if not (0 <= pH <= 14):
            print(f"Invalid pH: {pH}")
            return False
        do_duc = float(do_duc)
        if not (0 <= do_duc <= 1000):
            print(f"Invalid Do_duc: {do_duc}")
            return False
        nhiet_do = float(nhiet_do)
        if not (0 <= nhiet_do <= 100):
            print(f"Invalid Nhiet_do: {nhiet_do}")
            return False
        if not isinstance(khu_vuc, str) or not khu_vuc.strip():
            print(f"Invalid khu_vuc: {khu_vuc}")
            return False
        if not isinstance(kenh_song, str) or not kenh_song.strip():
            print(f"Invalid kenh_song: {kenh_song}")
            return False
        print("Validation passed")
        return True
    except (ValueError, TypeError) as e:
        print(f"Validation error: {e}")
        return False

def Data(data1, data2, data3, data4, data5, data6):
    data = {
        "pH": data1,
        "Do_duc": data2,
        "Nhiet_do": data3,
        "thoi_gian": data4,
        "khu_vuc": data5,
        "kenh_song": data6
    }
    print(f"Preparing JSON: {data}")
    params = json.dumps(data).encode()
    return params

def MyPostJson(params):
    req = request.Request('https://ai-dakt-3.onrender.com/update_post', method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("accept", "application/json")
    
    try:
        r = request.urlopen(req, data=params, timeout=10)
        response_data = r.read()
        print("POST response:", response_data.decode())
        return response_data
    except Exception as e:
        print(f"Error posting JSON data: {e}")
        return None

def my_get():
    try:
        req = request.Request('https://ai-dakt-3.onrender.com/get', method="GET")
        req.add_header("accept", "application/json")
        r = request.urlopen(req, timeout=10)
        response_data = r.read().decode()
        response_json = json.loads(response_data)
        print("GET response:", response_json)
        return response_json
    except Exception as e:
        print(f"Error getting data: {e}")
        return None

def main():
    print("Waiting for LoRa packets...")
    
    while True:
        # Receive LoRa packet with 5-second timeout
        packet = rfm9x.receive(timeout=5.0)
        
        if packet is not None:
            try:
                # Check RSSI
                rssi = rfm9x.last_rssi
                print(f"RSSI: {rssi} dB")
                
                # Decode packet to ASCII
                packet_text = str(packet, "ascii").strip()
                print(f"Raw packet: '{packet_text}'")
                
                # Expected format: pH,pH2,NTU,Temp,khu_vuc,kenh_song
                data_parts = packet_text.split(',')
                print(f"Split parts: {data_parts}")
                
                if len(data_parts) == 6:
                    pH1, pH2, do_duc, nhiet_do, khu_vuc, kenh_song = data_parts
                    print(f"Parsed: pH2={pH2}, Do_duc={do_duc}, Nhiet_do={nhiet_do}, khu_vuc={khu_vuc}, kenh_song={kenh_song}")
                    
                    # Validate received data using pH2
                    if validate_data(pH2, do_duc, nhiet_do, khu_vuc, kenh_song):
                        # Add timestamp
                        thoi_gian = strftime('%Y-%m-%d %H:%M:%S')
                        
                        # Prepare JSON data
                        params_json = Data(
                            float(pH2),
                            float(do_duc),
                            float(nhiet_do),
                            thoi_gian,
                            khu_vuc,
                            kenh_song
                        )
                        
                        # Post to server
                        post_json = MyPostJson(params_json)
                        if post_json is None:
                            print("Failed to post JSON data")
                        
                        # Get server response
                        receive_data = my_get()
                        if receive_data is None:
                            print("Failed to get server response")
                    else:
                        print("Invalid data received, skipping...")
                else:
                    print(f"Invalid data format, expected 6 values, got {len(data_parts)}")
            except Exception as e:
                print(f"Error processing packet: {e}")
        else:
            print("No packet received, continuing...")
            
        sleep(1)  # Small delay to prevent CPU overload

if __name__ == '__main__':
    main()