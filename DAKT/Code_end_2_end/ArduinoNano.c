#include <SPI.h>
#include <E:\Lora_Esp_pi4\arduino-LoRa-master\examples\LoRaSender\LoRa.h>

#include <OneWire.h>
#include <DallasTemperature.h>



// ====== Chân cảm biến ======
#define ONE_WIRE_BUS 4       // DS18B20 ở chân D4
#define phPin A1             // Cảm biến pH ở A1
const int turbidityPin = A0; // Cảm biến độ đục ở A0

// ====== Biến toàn cục ======
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

const float U0 = 3600.0;     // mV tại 0 NTU
float Um, f, NTU;

int buf[10], temp;
unsigned long int avgValue;

// ====== Thông tin khu vực và kênh ======
const String khu_vuc = "Go Vap";
const String kenh_song = "An Thong";

void setup() {
  Serial.begin(9600);
  while (!Serial);

  sensors.begin(); // Khởi tạo cảm biến nhiệt độ

  // Khởi tạo LoRa
  LoRa.setPins(10, 9, 2);  // NSS = D10, RESET = D9, DIO0 = D2
  if (!LoRa.begin(433E6)) {
    Serial.println("Lỗi khởi động LoRa!");
    while (1);
  }

  // Cấu hình LoRa để tăng khoảng cách
  LoRa.setSpreadingFactor(9);      // SF9: Tăng khoảng cách
  LoRa.setSignalBandwidth(125000); // BW 125 kHz
  LoRa.setCodingRate4(8);          // CR 4/8: Tăng độ bền tín hiệu
  LoRa.setTxPower(17);             // Công suất 20 dBm (gần tối đa)

  Serial.println("Thiết bị Nano đã sẵn sàng.");
}

void loop() {
  // ===== Đo độ đục =====
  int turbidityValue = analogRead(turbidityPin);
  Um = (turbidityValue / 1023.0) * 5000.0; // mV
  f = Um / U0;

  if (f >= 0.98 && f <= 1.0) {
    NTU = 0;
  } else {
    NTU = map(f * 100, 0, 100, 1000, 0);
  }

  // ===== Đo pH =====
  for (int i = 0; i < 10; i++) {
    buf[i] = analogRead(phPin);
    delay(10);
  }
  for (int i = 0; i < 9; i++) {
    for (int j = i + 1; j < 10; j++) {
      if (buf[i] > buf[j]) {
        temp = buf[i];
        buf[i] = buf[j];
        buf[j] = temp;
      }
    }
  }
  avgValue = 0;
  for (int i = 2; i < 8; i++) {
    avgValue += buf[i];
  }

  float voltage = (float)avgValue * 5.0 / 1024.0 / 6;
  float pHValue = 4 * voltage;

  // Kiểm tra pH hợp lệ
  if (pHValue < 0 || pHValue > 14 || isnan(pHValue)) {
    pHValue = 7.0; // Giá trị mặc định nếu pH không hợp lệ
    Serial.println("pH không hợp lệ, dùng mặc định 7.0");
  }

  // ===== Đo nhiệt độ =====
  sensors.requestTemperatures();
  float tempC = sensors.getTempCByIndex(0);
  if (tempC == DEVICE_DISCONNECTED_C) {
    tempC = 25.0; // Giá trị mặc định nếu cảm biến lỗi
    Serial.println("Nhiệt độ không hợp lệ, dùng mặc định 25.0");
  }

  // ===== Tạo chuỗi dữ liệu =====
  String sendData = String(pHValue, 2) + "," + String(pHValue, 2) + "," + String(NTU, 2) + "," + 
                    String(tempC, 2) + "," + khu_vuc + "," + kenh_song;

  Serial.println("Gửi: " + sendData);

  // Gửi qua LoRa
  LoRa.beginPacket();
  LoRa.print(sendData);
  LoRa.endPacket();

  delay(5000); // Gửi mỗi 5 giây
}