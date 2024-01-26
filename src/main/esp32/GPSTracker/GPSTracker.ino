/**
   GPSTracker by BikeAtor (WoMoAtor) Version 2.1

   Original Code: https://github.com/vshymanskyy/TinyGSM/tree/master/examples/AllFunctions

   This project is released under The GNU Lesser General Public License (LGPL-3.0)

   Version 2.1:
   - config sleeptime
   Version 2.0:
   - Open GPRS afer getting position
   - Use ArduinoHttpClient for connection to webserver
   Version 1.0:
   - Working
*/
/**************************************************************

   TinyGSM Getting Started guide:
     https://tiny.cc/tinygsm-readme

   NOTE:
   Some of the functions may be unavailable for your modem.
   Just comment them out.
   https://simcom.ee/documents/SIM7600C/SIM7500_SIM7600%20Series_AT%20Command%20Manual_V1.01.pdf
   This project is released under The GNU Lesser General Public License (LGPL-3.0)
 **************************************************************/

#include "secrets.h"

#define TINY_GSM_MODEM_SIM7600

// Set serial for debug console (to the Serial Monitor, default speed 115200)
#define SerialMon Serial

// Set serial for AT commands (to the module)
// Use Hardware Serial on Mega, Leonardo, Micro
#define SerialAT Serial1


// Define the serial console for debug prints, if needed
#define TINY_GSM_DEBUG SerialMon

/*
   Tests enabled
*/
#define TINY_GSM_TEST_GPRS true
#define TINY_GSM_TEST_GPS true
#define TINY_GSM_TEST_TEMPERATURE true
// powerdown modem after tests
#define TINY_GSM_POWERDOWN true


// Your GPRS credentials, if any
const char apn[] = APN;
// const char apn[] = "ibasis.iot";
const char gprsUser[] = GPRS_USER;
const char gprsPass[] = GPRS_PASS;


#define uS_TO_S_FACTOR 1000000ULL /* Conversion factor for micro seconds to seconds */

#define UART_BAUD 115200

#define MODEM_TX 27
#define MODEM_RX 26
#define MODEM_PWRKEY 4
#define MODEM_DTR 32
#define MODEM_RI 33
#define MODEM_FLIGHT 25
#define MODEM_STATUS 34

#define SD_MISO 2
#define SD_MOSI 15
#define SD_SCLK 14
#define SD_CS 13

#define LED_PIN 12

#define ADC_PIN 35
int vref = 1100;

#include <SPI.h>
#include <SD.h>
#include <Ticker.h>
#include <TinyGsmClient.h>
#define USE_HTTP_CLIENT true
#ifdef USE_HTTP_CLIENT
#include <ArduinoHttpClient.h>
#endif
#ifdef GPS_DATA_USE_HTTPS
#ifdef USE_WIFI_CLIENT
#include <WiFiClientSecure.h>
#endif
#endif

#ifdef DUMP_AT_COMMANDS
#include <StreamDebugger.h>
StreamDebugger debugger(SerialAT, SerialMon);
TinyGsm modem(debugger);
#else
TinyGsm modem(SerialAT);
#endif

void setup() {
  // Set console baud rate
  SerialMon.begin(115200);
  delay(10);

  // Set GSM module baud rate
  SerialAT.begin(UART_BAUD, SERIAL_8N1, MODEM_RX, MODEM_TX);

  /*
    The indicator light of the board can be controlled
  */
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);

  /*
    MODEM_PWRKEY IO:4 The power-on signal of the modulator must be given to it,
    otherwise the modulator will not reply when the command is sent
  */
  pinMode(MODEM_PWRKEY, OUTPUT);
  digitalWrite(MODEM_PWRKEY, HIGH);
  delay(300);  //Need delay
  digitalWrite(MODEM_PWRKEY, LOW);

  /*
    MODEM_FLIGHT IO:25 Modulator flight mode control,
    need to enable modulator, this pin must be set to high
  */
  pinMode(MODEM_FLIGHT, OUTPUT);
  digitalWrite(MODEM_FLIGHT, HIGH);

  // Initialize SDCard
  SPI.begin(SD_SCLK, SD_MISO, SD_MOSI, SD_CS);
  if (!SD.begin(SD_CS)) {
    Serial.println("SDCard MOUNT FAIL");
  } else {
    uint32_t cardSize = SD.cardSize() / (1024 * 1024);
    String str = "SDCard Size: " + String(cardSize) + "MB";
    Serial.println(str);
  }
}

void light_sleep(uint32_t sec) {
  esp_sleep_enable_timer_wakeup(sec * 1000000ULL);
  esp_light_sleep_start();
}

void send_data_http(String parameter) {
  TinyGsmClient client(modem, 0);
  DBG("Connecting to", GPS_DATA_SERVER);
#ifdef USE_HTTP_CLIENT
  HttpClient http(client, GPS_DATA_SERVER, GPS_DATA_PORT);

  String resource = GPS_DATA_PATH + parameter;
  DBG("Request:", resource);
  int err = http.get(resource);
  if (err != 0) {
    DBG("failed to connect", err);
    return;
  }
  int status = http.responseStatusCode();
  DBG("Response status code:", status);

  String body = http.responseBody();
  DBG("Response body:", body);

  http.stop();
  client.stop();
#else
  if (!client.connect(GPS_DATA_SERVER, GPS_DATA_PORT)) {
    DBG("... failed");
  } else {
    // Make a HTTP GET request:
    client.print(String("GET ") + GPS_DATA_PATH + parameter + " HTTP/1.0\r\n");
    client.print(String("Host: ") + GPS_DATA_SERVER + "\r\n");
    client.print("Connection: close\r\n\r\n");

    // Wait for data to arrive
    uint32_t start = millis();
    while (client.connected() && !client.available() && millis() - start < 30000L) {
      delay(100);
    };

    // Read data
    start = millis();
    while (client.connected() && millis() - start < 5000L) {
      while (client.available()) {
        SerialMon.write(client.read());
        start = millis();
      }
    }
    client.stop();
  }
#endif
}

#ifdef GPS_DATA_USE_HTTPS
void send_data_https(String msg) {
  DBG("Connecting to", GPS_DATA_SERVER);
#ifdef USE_HTTP_CLIENT
  TinyGsmClientSecure client(modem);
  HttpClient http(client, GPS_DATA_SERVER, GPS_DATA_PORT);

  http.connectionKeepAlive();  // Currently, this is needed for HTTPS

  String resource = GPS_DATA_PATH + msg;
  int err = http.get(resource);
  if (err != 0) {
    SerialMon.println(F("failed to connect"));
    delay(10000);
    return;
  }
  http.stop();
#endif

#ifdef USE_WIFI_CLIENT
  // Use WiFiClientSecure class to create TLS connection
  WiFiClientSecure client;

  IPAddress address;
  if (!WiFi.hostByName(GPS_DATA_SERVER, address)) {
    DBG("Could not resolve", GPS_DATA_SERVER);
  }

  if (!client.connect(GPS_DATA_SERVER, GPS_DATA_PORT)) {
    DBG("### connection failed");
    return;
  }

  //  if (client.verify(fingerprint, host)) {
  //    Serial.println("certificate matches");
  //  } else {
  //    Serial.println("certificate doesn't match");
  //  }

  DBG("requesting URL: ", GPS_DATA_PATH);

  client.print(String("POST ") + GPS_DATA_PATH + " HTTP/1.1\r\n"                          //
               + "Host: " + GPS_DATA_SERVER + "\r\n"                                      //
               + "Connection: close\r\n"                                                  //
               + "Accept: */*\r\n"                                                        //
               + "User-Agent: Mozilla/4.0 (compatible; esp8266 Lua; Windows NT 5.1)\r\n"  //
               + "Content-Type: application/json;charset=utf-8\r\n" +                     //
               // "Authorization: Bearer "+cloudDeviceToken+"\r\n" + //
               "Content-Length: " + msg.length() + "\r\n"  //
               + "\r\n"                                    //
               + msg + "\r\n");

  Serial.println("request sent");
  unsigned long timeout = millis();
  while (client.available() == 0) {
    if (millis() - timeout > 5000) {
      DBG("### Client Timeout");
      client.stop();
      return;
    }
  }

  // Read all the lines of the reply from server and print them to Serial
  while (client.available()) {
    String line = client.readStringUntil('\r');
    DBG(line);
  }
  client.stop();
#endif
}
#endif


void connect_gprs() {
#if TINY_GSM_TEST_GPRS
  /*  Preferred mode selection : AT+CNMP
        2 ?? Automatic
        13 ?? GSM Only
        14 ?? WCDMA Only
        38 ?? LTE Only
        59 ?? TDS-CDMA Only
        9 ?? CDMA Only
        10 ?? EVDO Only
        19 ?? GSM+WCDMA Only
        22 ?? CDMA+EVDO Only
        48 ?? Any but LTE
        60 ?? GSM+TDSCDMA Only
        63 ?? GSM+WCDMA+TDSCDMA Only
        67 ?? CDMA+EVDO+GSM+WCDMA+TDSCDMA Only
        39 ?? GSM+WCDMA+LTE Only
        51 ?? GSM+LTE Only
        54 ?? WCDMA+LTE Only
  */
  String ret;
  //    do {
  //        ret = modem.setNetworkMode(2);
  //        delay(500);
  //    } while (ret != "OK");
  ret = modem.setNetworkMode(2);
  DBG("setNetworkMode:", ret);


  //https://github.com/vshymanskyy/TinyGSM/pull/405
  uint8_t mode = modem.getGNSSMode();
  DBG("GNSS Mode:", mode);

  /**
      CGNSSMODE: <gnss_mode>,<dpo_mode>
      This command is used to configure GPS, GLONASS, BEIDOU and QZSS support mode.
      gnss_mode:
          0 : GLONASS
          1 : BEIDOU
          2 : GALILEO
          3 : QZSS
      dpo_mode :
          0 disable
          1 enable
  */
  // modem.setGNSSMode(1, 1);
  modem.setGNSSMode(0, 1);
  light_sleep(1);

  String name = modem.getModemName();
  DBG("Modem Name:", name);

  String modemInfo = modem.getModemInfo();
  DBG("Modem Info:", modemInfo);

  // Unlock your SIM card with a PIN if needed
  if (GSM_PIN && modem.getSimStatus() != 3) {
    modem.simUnlock(GSM_PIN);
  }

  DBG("Waiting for network...");
  if (!modem.waitForNetwork(600000L)) {
    light_sleep(10);
    return;
  }

  if (modem.isNetworkConnected()) {
    DBG("Network connected");
  }

  DBG("Connecting to", apn);
  if (!modem.gprsConnect(apn, gprsUser, gprsPass)) {
    light_sleep(10);
    return;
  }

  bool res = modem.isGprsConnected();
  DBG("GPRS status:", res ? "connected" : "not connected");

  String ccid = modem.getSimCCID();
  DBG("CCID:", ccid);

  String imei = modem.getIMEI();
  DBG("IMEI:", imei);

  String imsi = modem.getIMSI();
  DBG("IMSI:", imsi);

  String cop = modem.getOperator();
  DBG("Operator:", cop);

  IPAddress local = modem.localIP();
  DBG("Local IP:", local);

  int csq = modem.getSignalQuality();
  DBG("Signal quality:", csq);
#endif
}

void disconnect_gprs() {
#if TINY_GSM_TEST_GPRS
  modem.gprsDisconnect();
  // wait for shutdown
  light_sleep(5);
  if (!modem.isGprsConnected()) {
    DBG("GPRS disconnected");
  } else {
    DBG("GPRS disconnect: Failed.");
  }
#endif
}

void get_gps_data() {
#if TINY_GSM_TEST_GPS && defined TINY_GSM_MODEM_HAS_GPS
  DBG("Enabling GPS/GNSS/GLONASS");
  modem.enableGPS();
  light_sleep(2);

  float lat2 = 0;
  float lon2 = 0;
  float speed2 = 0;
  float alt2 = 0;
  int vsat2 = 0;
  int usat2 = 0;
  float accuracy2 = 0;
  int year2 = 0;
  int month2 = 0;
  int day2 = 0;
  int hour2 = 0;
  int min2 = 0;
  int sec2 = 0;
  DBG("Requesting current GPS/GNSS/GLONASS location");
  int max_tries = 20;
  bool first = true;
  for (int i = 1; i <= max_tries; i++) {
    digitalWrite(LED_PIN, !digitalRead(LED_PIN));
    DBG("try: " + String(i));
    if (modem.getGPS(&lat2, &lon2, &speed2, &alt2, &vsat2, &usat2, &accuracy2,
                     &year2, &month2, &day2, &hour2, &min2, &sec2)) {
      if (first) {
        // do not use first position. its mostly not good
        first = false;
        DBG("Do not use first position. Accuracy:", accuracy2);
        // some extra sleep
        light_sleep(5);
      } else {
        DBG("Latitude:", String(lat2, 8), "\tLongitude:", String(lon2, 8));
        DBG("Speed:", speed2, "\tAltitude:", alt2);
        DBG("Visible Satellites:", vsat2, "\tUsed Satellites:", usat2);
        DBG("Accuracy:", accuracy2);
        String date = String(year2) + "-" + month2 + "-" + day2 + " " + hour2 + ":" + min2 + ":" + sec2;
        DBG("Time:", date);
        uint16_t v = analogRead(ADC_PIN);
        float battery_voltage = ((float)v / 4095.0) * 2.0 * 3.3 * (vref / 1000.0);

        String parameter = "?lat=" + String(lat2, 8)
                           + "&lon=" + String(lon2, 8)
                           + "&alt=" + alt2
                           + "&spd=" + speed2
                           + "&acc=" + String(accuracy2)
                           + "&vol=" + String(battery_voltage);
#if defined TINY_GSM_MODEM_HAS_TEMPERATURE
        float temp = modem.getTemperature();
        DBG("Chip temperature:", temp);
        parameter += "&tmp=" + String(temp);
#endif
        connect_gprs();
#ifdef GPS_DATA_USE_HTTPS
        send_data_https(parameter);
#else
        send_data_http(parameter);
#endif
        break;
      }
    }
    if (i == max_tries) {
      DBG("Position not found. Going to sleep");
      break;
    }
    light_sleep(5);
  }
  // DBG("Retrieving GPS/GNSS/GLONASS location again as a string");
  // String gps_raw = modem.getGPSraw();
  // DBG("GPS/GNSS Based Location String:", gps_raw);
  DBG("Disabling GPS");
  modem.disableGPS();
#endif
}

void loop() {
  // Restart takes quite some time
  // To skip it, call init() instead of restart()
  DBG("Initializing modem...");
  if (!modem.init()) {
    DBG("Failed to restart modem, delaying 10s and retrying");
    return;
  }

  get_gps_data();

  disconnect_gprs();

#if TINY_GSM_POWERDOWN
  // Try to power-off (modem may decide to restart automatically)
  // To turn off modem completely, please use Reset/Enable pins
  modem.poweroff();
  DBG("Poweroff.");
#endif

  SerialMon.printf("End of tests. Enable deep sleep , Will wake up in %d seconds", TIME_TO_SLEEP);

  // Wait for modem to power off
  light_sleep(5);

  esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP * uS_TO_S_FACTOR);
  delay(200);
  esp_deep_sleep_start();

  while (1)
    ;
}
