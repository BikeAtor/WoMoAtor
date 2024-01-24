// set GSM PIN, if any
#define GSM_PIN             "1234"
// Your GPRS credentials, if any
#define APN		 "pinternet.interkom.de";
// const char apn[] = "ibasis.iot";
#define GPRS_USER "";
#define GPRS_PASS "";

// server for HTTP-Requests
#define SERVER_GPS_DATA "MYSERVER";
#define PORT_GPS_DATA 80;
// Resource at server to call. parameter will be added ?lat=XXX&lon=XXX&alt=XXX&spd=XXX&vol=XXX&tmp=XXX
// spd=speed in knots or km/h?
// vol=voltage 0 during connected to power
// tmp=temperature (°C?)
#define RESOURCE_GPS_DATA "/echo.php";
