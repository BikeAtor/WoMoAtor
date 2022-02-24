# WoMoAtor
Überwachung und Steuerung eines Wohnmobils mit dem Raspberry Pi und Python3.

Das Projekt befindet sich in der Entwicklungsphase. Es können ständig gravierende Änderungen vorgenommen werden.

Die Hauptklasse für die komplette Steuerung ist derzeit noch nicht veröffentlicht. Die einzelnen Module können jedoch auch unabhängig davon verwendet werden. Viele Dateien können auch direkt gestartet werden (main()).

## Module
Folgende Module existieren:
* Überwachung der LiFePo3-Batterie von [Supervolt](https://supervolt.de/) ( [Einbaubericht](Einbau_Supervolt.md) ) ( Ist auch unter [Windows](src/main/python/supervolt/README_windows.md) nutzbar )
* Überwachung der Fahrzeugbatterie mit [BatteryGuard](https://www.battery-guard.net/)
* Überwachung der Temperaturen mit Bluetooth-LE fähigen Sensoren
* Reifendrücküberwachung TPMS mit DVB-T-Empfänger
* GPS


Folgende Module sind geplant:

* Gassensor und  Bewegungsmelder (Arduino Nano mit MQ-2, IR oder Radarsensor)

Im Laufe der Zeit kommen mehr Module hinzu.

## Verwendete Pythonmodule
Verwendete Python-Module (evtl unvollständig):
- smopy
- pynmea2
- (bluepy)
- bleak
- bleson
- cairosvg
- schedule
- pillow
- (pyscreenshot)
- (opencv-contrib-python)
- (pydbus)

Hier das Kommando zum installieren der benötigten Module:

(sudo) pip3 install --upgrade setuptools

Auf Windows-Systemen bluepy weglassen, da diese nicht unterstütz werden. Weiter muss [MSYS2](https://www.msys2.org/) installiert werden und dort mit "pacman -S mingw-w64-x86_64-python3-gobject" die Bibliotheken für die graphische Ausgabe (GUI). Danach muss %PATH% in den Umgebungsvariablen um <MSYS2>\mingw64\bin erweitert werden um die DLL-Dateien zu finden.
Alternativ kann der Pfad auch in Python gesetzt werden.

(sudo) pip3 install bluepy bleak bleson cairosvg schedule pillow

(sudo) pip3 install pyscreenshot opencv-contrib-python pydbus

## Konfiguration mit JSON
Die Konfiguration erfolgt per JSON. Weitere Informationen zur Konfiguration befindet sich im jeweiligen Modul.

	{
		"system": {
			"name": "WoMoAtor",
			"version": "V0.1"
		},
		"notification": {
			"emailToAddresses": "b@b.c",
			"emailFromAddress": "a@b.c",
			"emailServer": "smtp.email",
			"emailPort": 587,
			"emailPassword": "bubu",
			"dataURL": "https://wo auch immer"
		}
	}
