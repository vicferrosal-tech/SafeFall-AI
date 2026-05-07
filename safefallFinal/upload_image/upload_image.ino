#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>
//^ llibreries necessaries pel codi
//configuració del wifi (dades mobils del mobil)
const char* ssid = "Isaac";
const char* password = "12185f4e0c2c";
//IPAddress local_IP(10, 138, 91, 216); estableix una IP fixa per a la càmera.
String heartbeatName = "http://10.115.45.237:5001/heartbeat";
unsigned long lastHeartbeat = 0;
const unsigned long heartbeatInterval = 10000; // 10 segons
String serverName = "http://10.115.45.237:5001/upload"; // "url" del servidor (rasperry) 

//configuració dels pins de la ESP32-CAM
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

//variables per a calcular el temps d'enviament d'imatges
unsigned long lastCapture = 0;
const unsigned long captureInterval = 5000; // interval de 5 segons per l'enviament d'imatges

void setup() {
  Serial.begin(115200);
  Serial.println("Iniciando cámara...");

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG; // el format de compressió de la imatge, jpeg es un format de lleuger i adequat per a la camera. 
  config.frame_size = FRAMESIZE_VGA;    // especifica la mida de la imatge VGA = 640 x 480 px 
  config.jpeg_quality = 12;             // qualitat de la imatge, com a més baix el número millor qualitat
  config.fb_count = 1;
//comprovació del estat de la ESP32-CAM
  if (esp_camera_init(&config) != ESP_OK) {
    Serial.println("Error al iniciar la cámara");
    while(true);
  }
//Funcio bucle que inicia la connexió al wifi (preguntar)
  Serial.println("Conectando a WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado");
  Serial.print("IP local: ");
  Serial.println(WiFi.localIP());
}
//Es l'interval que ha d'esperar la camara per enviar les imatges al servidor (rasperry)
void loop() {
  unsigned long now = millis();

  // 1. BLOC DE LA FOTOGRAFIA
  if (now - lastCapture > captureInterval) {
    sendPhoto();
    lastCapture = now;
  }

  // 2. NOU BLOC DEL HEARTBEAT (Batec)
  if (now - lastHeartbeat > heartbeatInterval) {
    if (WiFi.status() == WL_CONNECTED) {
      WiFiClient client; // Client normal, sense "Secure"
      HTTPClient http;
      http.begin(client, heartbeatName); // Truquem a la ruta /heartbeat
      
      http.addHeader("X-API-KEY", "k3_2f@c0n_32pcam");

      int httpResponseCode = http.GET();
      if(httpResponseCode > 0){
        Serial.printf("Heartbeat enviat. Resposta: %d\n", httpResponseCode);
      } else {
        Serial.println("Error enviant Heartbeat");
      }
      http.end();
    }
    lastHeartbeat = now;
  }
}

// === FUNCIÓ PER ENVIAR LA FOTO ===
void sendPhoto() {
  Serial.println("Capturando imagen...");
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Error al capturar");
    return;
  }

  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client; // Modificat a client normal (HTTP) per estabilitat
    HTTPClient http;
    http.begin(client, serverName);

    http.addHeader("X-API-KEY", "k3_2f@c0n_32pcam");
    http.addHeader("Content-Type", "image/jpeg");

    int httpResponseCode = http.POST(fb->buf, fb->len);
    if (httpResponseCode > 0) {
      Serial.printf("Imagen enviada. Respuesta: %d\n", httpResponseCode);
    } else {
      Serial.printf("Error en POST: %s\n", http.errorToString(httpResponseCode).c_str());
    }
    http.end();
  } else {
    Serial.println("WiFi no conectado");
  }

  esp_camera_fb_return(fb);
}