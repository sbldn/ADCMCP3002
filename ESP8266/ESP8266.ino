/*
 * Sketch: ESP8266_LED_Control_02
 * Control an LED from a web browser
 * Intended to be run on an ESP8266
 * 
 * connect to the ESP8266 AP then
 * use web broswer to go to 192.168.4.1
 * 
 */
#include <ArduinoJson.h>
#include <ArduinoJson.hpp>
#include <SPI.h>
#include <ESP8266WiFi.h>

const char WiFiPassword[] = "mosaicosensorial";
const char AP_NameChar[] = "MosaicoSensorial";

const int CS_PIN = 15; // Pin para CS del MCP3002
const int ledWIFI = 4; // Pin del LED para indicar estado de WIFI
const int ledON = 2;   // Pin del LED de encendido
const int LED_Pin = 4;

double average1, average2;
int num_samples = 10; // Número de muestras para promedio
StaticJsonDocument<200> doc;

bool wifiLedState = true; // Estado actual del LED de WIFI
bool onLedState = true;  

WiFiServer server(80);

String header = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n";
String html_1 = "<!DOCTYPE html><html><head><title>LED Control</title></head><body><div id='main'><h2>LED Control</h2>";
String html_2 = "<form id='F1' action='LEDON'><input class='button' type='submit' value='LED ON' ></form><br>";
String html_3 = "<form id='F2' action='LEDOFF'><input class='button' type='submit' value='LED OFF' ></form><br>";
String html_4 = "<form action='TEST'>";
String html_5 = "<label for='SSID'>SSID:</label><br><input type='text' id='ssid' name='SSID' value=''><br>";
String html_6 = "<label for='pass'>PASS:</label><br><input type='text' id='pass' name='PASS' value=''><br><br>";
String html_7 = "<input type='submit' value='enviar'></form>";
String html_8 = "</div></body></html>";

String request = "";
unsigned long previousMillis = 0;
const long interval = 1000; // Intervalo de 1 segundo

void setup() 
{
    Serial.begin(115200);
    SPI.begin();

    pinMode(LED_Pin, OUTPUT); 
    pinMode(CS_PIN, OUTPUT);
    pinMode(ledWIFI, OUTPUT);
    pinMode(ledON, OUTPUT);
    digitalWrite(CS_PIN, HIGH); // Desactivar chip select

    WiFi.softAP(AP_NameChar, WiFiPassword);
    server.begin();
    
    turnOnRoutine(); // Iniciar la rutina de encendido de LEDs al inicio
}

void loop() 
{
    unsigned long currentMillis = millis();
    
    // Procesar comandos del puerto serie
    if (Serial.available() > 0) {
        processSerialCommand();
    }
    
    // Leer y promediar los valores del ADC a intervalos regulares
    if (currentMillis - previousMillis >= interval) {
        previousMillis = currentMillis;
        read_average_adc(num_samples, average1, average2);
        createJson(average1, average2);
    }

    // Procesar peticiones HTTP
    WiFiClient client = server.available();
    if (client) {
        processHttpRequest(client);
    }
}

void processSerialCommand() {
    char command = Serial.read();
    
    switch (command) {
        case '0':
            digitalWrite(ledWIFI, LOW);
            wifiLedState = false;
            break;
        case '1':
            digitalWrite(ledWIFI, HIGH);
            wifiLedState = true;
            break;
        case '2':
            digitalWrite(ledON, LOW);
            onLedState = false;
            break;
        case '3':
            digitalWrite(ledON, HIGH);
            onLedState = true;
            break;
    }
}

void processHttpRequest(WiFiClient &client) {
    request = client.readStringUntil('\r');
    if (request.indexOf("LEDON") > 0) {
        digitalWrite(LED_Pin, HIGH);
    } else if (request.indexOf("LEDOFF") > 0) {
        digitalWrite(LED_Pin, LOW);
    } else if (request.indexOf("TEST") > 0) {
        Serial.println(request);
    }
    client.flush();

    client.print(header);
    client.print(html_1);
    client.print(html_2);
    client.print(html_3);
    client.print(html_4);
    client.print(html_5);
    client.print(html_6);
    client.print(html_7);
    client.print(html_8);
    delay(5);
}

void read_average_adc(int samples, double &result1, double &result2) {
    double aux1 = 0;
    double aux2 = 0;

    for (int i = 0; i < samples; i++) {
        aux1 += readMCP3002(0);
        aux2 += readMCP3002(1);
    }

    result1 = aux1 / samples;
    result1 = ((result1 * 5 / 1023) - (1.51)) * 17 / 1.01;
    result2 = aux2 / samples;
}

void createJson(double temperature, double light) {
    doc["temperature"] = temperature;
    doc["luminosity"] = light;
    serializeJson(doc, Serial);
    Serial.println();
}

void turnOnRoutine() {
    // Parpadear LEDs durante la rutina de encendido
    for (int i = 0; i <= 5; i++) {
        digitalWrite(ledWIFI, LOW);
        digitalWrite(ledON, LOW);
        delay(1000);
        digitalWrite(ledWIFI, HIGH);
        digitalWrite(ledON, HIGH);
        delay(1000);
    }
}

uint16_t readMCP3002(uint8_t channel) {
    // Validar el canal
    if (channel > 1) return 0;

    // Seleccionar el canal
    uint8_t command = 0b01101000 | (channel << 4);

    digitalWrite(CS_PIN, LOW); // Activar chip select

    // Enviar el comando y recibir la respuesta
    uint8_t response1 = SPI.transfer(command);
    uint8_t response2 = SPI.transfer(0x00);

    digitalWrite(CS_PIN, HIGH); // Desactivar chip select

    // Combinar las dos respuestas para obtener el valor del ADC
    uint16_t result = ((response1 & 0x03) << 8) | response2;

    return result;
}

