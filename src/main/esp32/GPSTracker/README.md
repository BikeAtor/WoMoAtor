# WoMoAtor GPSTracker
Der Tracker verwendet ein [LILYGO T-SIM7600E](https://www.lilygo.cc/products/t-sim7600) um die GPS-Daten zu ermitteln und über Mobilfunk (LTE) an einen privaten Server zu übertragen.

Der ESP32-Chip wird alle 5 Minuten aufgeweckt (konfigurierbar), die GPS-Position ermittelt und die Daten über das Mobilfunknetz übertragen. Sollte einer der Schritte nicht funktionieren, so wird nach einiger Zeit abgebrochen und später ein neuer Versuch gestartet.

## Sicherheit
Die Daten werden per HTTP (HTTPS ist ~~derzeit~~ nicht möglich) übertragen. D.h. die Daten werden unverschlüsselt übertragen und könnten bei der Übertragung ohne Probleme abgehört werden.

## Konfiguration
Die Konfiguration erfolgt in der Datei secrets.h. Hierzu einfach den Inhalt von secrets_example.h kopieren und entsprechend ändern.

## Installation
Der Code kann einfach mit der Arduino-IDE geflasht werden. Als Board "ESP32 Dev Module" auswählen.
Zusätzliche Bibliotheken:
- TinyGSM
- AdruinoHttpClient
- ?

Zum Flashen am T-SIM den USB-Port mit der Bezeichung "TTL" verwenden.

## SIM-Karte
Ich habe eine kostenlose SIM von Netzclub verwendet.

## Webserver
Für die Übertragung der Daten wird ein eigener Webserver mit fester IP/DNS-Namen und der Möglichkeit diesen per HTTP zu erreichen. Alternativ reicht auch ein reiner Socketlistener aus, da HTTP nicht allzu schwer zu parsen ist.
Eine Bespieldatei für z.B. Apache ist in echo.php zu finden.

## TODO
- Man könnte eine evtl. vorhandene Wifi-Verbindung benutzen.
- ~~Wenn sich die Position nicht (stark) verändert hat braucht man diese nicht senden.~~
Verworfen, da man so sehen kann, ob die Verbindung noch funktioniert. Man kann unterscheiden zwischen "nicht funktionsfähig" und "nicht bewegt".

## Lizenz
GNU Lesser General Public License (LGPL-3.0)