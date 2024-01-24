# WoMoAtor GPSTracker
DerTracker verwendet ein [LILYGO T-SIM7600E](https://www.lilygo.cc/products/t-sim7600) um die GPS-Daten zu ermitteln und über Mobilfunk zu übertragen.

Hierbei wird ein Konfigurierbarer Server (Siehe secrets_example.h) per HTTP angesprochen und die Daten an den URL angehängt (HTTPS ist derzeit nicht möglich). D.h. ein Potentieller Angreifer kann die Daten mitlesen. Da diese aber nicht an einen allgemeinen Server gehen sind die Daten für Hacker eher uninteressant.

Der ESP32-Chip wird alle 5 Minuten aufgeweckt, es wird eine Mobilfunkverbindung aufgebaut, die GPS-Position ermittelt und die Daten übertragen. Sollte einer der Schritte nicht funktionieren, so wird nach einiger Zeit abgebrochen.

## Konfiguration
Die Konfiguration erfolt in der Datei secrets.h. Hierzu einfach den Inhalt von secrets_example.h kopieren und entsprechend abändern.

## Installation
Der Code kann einfach mit der Arduino-IDE geflasht werden. Als Board "ESP32 DEv Module" auswählen.

## SIM-Karte
Ich habe eine kostenlose SIM von Netzclub verwndet.