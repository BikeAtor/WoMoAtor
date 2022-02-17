# Reifendruckkontrollsystem (RDKS/TPMS)
Das Modul unterstützt die Reifendrucksensoren von Schrader.

Hierzu wird ein DVB-T USB-Stick benötigt (bei [Amazon](https://www.amazon.de/dp/B07DJT5NHD)).

Dei Reifendrucksensoren senden bei Fahrzeugstillstand nur ca. 1x pro Tag. Also benötigt man evtl. Geduld.

## Konfiguration mit JSON
Hier ein Auszug aus der JSON-Konfiguration:

pressure_min und pressure_max werden derzeit nicht verwendet.

	"tpms": {
		"icon_filename": "pic/caravan-svgrepo-com.png",
		"pressure_min": 3.9,
		"pressure_max": 5.5,
		"FL": { "id": "1ED4440" },
		"FR": { "id": "1ED3C7B" },
		"BL": { "id": "1F5C7C7" },
		"BR": { "id": "1ED32EB" }
	}