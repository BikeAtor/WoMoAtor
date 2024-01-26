// set GSM PIN, if any
#define GSM_PIN             "1234"
// Your GPRS credentials, if any
#define APN		 "pinternet.interkom.de"
// const char apn[] = "ibasis.iot"
#define GPRS_USER ""
#define GPRS_PASS ""

// server for HTTP-Requests
#define GPS_DATA_SERVER "MYSERVER";
// normally HTTP = 80, HTTPS = 443
#define GPS_DATA_PORT 80
// HTTPS is not possible with LILYGO 7600
// #define GPS_DATA_USE_HTTPS true
// Resource at server to call. parameter will be added ?lat=XXX&lon=XXX&alt=XXX&spd=XXX&vol=XXX&tmp=XXX
// spd=speed in knots or km/h?
// vol=voltage 0 during connected to power
// tmp=temperature (°C?)
#define GPS_DATA_PATH "/echo.php"

// See all AT commands, if wanted
// #define DUMP_AT_COMMANDS
