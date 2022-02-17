# Temperatursensoren
Das Modul unterstützt verschiedene Temperatursensoren, welche über Bluetooth Low Energy (BLE) ausgelesen werden können.
Zum Teil wird auch der Zustand der Batterie angezeigt. Die Anzeige befindet sich noch im Teststatus und wird daher nicht stimmen.
Sollte der Sensor Historien speichern, können diese nicht abgerufen werden.

Folgende Sensoren werden unterstützt:
- **Brifit** (bei [Amazon](https://www.amazon.de/dp/B08GWVLXZ3)). Die Thermometer sind günstig und arbeiten sehr zuverlässig. Die Anzeige ist jedoch sehr klein und kann somit nicht gut abgelesen werden. Selbständiges Versenden der Daten [^1].
- **Azarton** (bei [Amazon](https://www.amazon.de/dp/B094CRSR99)). Der Thermometer hat ein großes e-Ink-Display. D.h. es kann sehr gut abgelesen werden. Bei meinen Tests hat die Batterie (CR-3032) jedoch nur ca. 3-4 Wochen durchgehalten. Daten müssen abgefragt werden [^2].
- **Inkbird TH-1** (bei [Amazon](https://www.amazon.de/dp/B07DRC4M88)). Es funktioniert sowohl die Variante mit und ohne Display. Vorteil ist hier, dass ein externen Fühler angeschlossen werden kann um z.B. die Temperatur von Flüssigkeiten zu messen oder auch nach Aussen z.B. unter das Fahrzeug verlegt werden kann.  Selbständiges Versenden der Daten [^1].
- **Govee** (bei [Amazon](https://www.amazon.de/dp/B08Y8XV8ST)).  Selbständiges Versenden der Daten [^1].
- **Mi-Sensor**. Es wird die alte, runde Version unterstützt. Ob einer der vielen Clones funktionieren kann ich nicht sagen. Der Sensor muss aktiv abgefragt werden, was die Zuverlässigkeit etwas einschränkt. Daten müssen abgefragt werden [^2].

Folgende Sensoren werden nicht unterstützt, obwohl Code vorhanden ist:
- **Inkbird TH-2** (bei [Amazon](https://www.amazon.de/dp/B08SQS74XP) wird derzeit **nicht unterstützt**, da das Auslesen des Sensors nicht funktioniert.


[^1]: Der Sensor sendet ohne Aufforderung alle paar Sekunden die ausgelesenen Daten.

[^2]: Die Daten müssen aktiv vom Sensor abgeholt werden. Hierzu wird eine Verbindung hergestellt und über Kommandos die Daten ausgelesen.

## Konfiguration mit JSON
Hier ein Auszug aus der JSON-Konfiguration (unvollständig):

	"sensors": [
		{
			"classname": "ble_bluetooth_sensor.AzartonSensor",
			"name": "Kühlschrank",
			"id": "fridge",
			"jsonPrefix": "Kuehlschrank",
		}
	]