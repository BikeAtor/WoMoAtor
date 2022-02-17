#!/usr/bin/env python3

import sys
sys.path.append('lib')

import os
import logging
import threading
import time
import serial
# GPS
import serial
import pynmea2


class GPS():
    port = None
    callbackAfterData = None
    baudrate = 9600
    
    position = None
    speedkmh = None
    
    def __init__(self,
                 jsonConfig=None,
                 port=None,
                 callbackAfterData=None):
        self.port = port
        self.callbackAfterData = callbackAfterData
        self.fromJSONConfig(jsonConfig)
        threading.Thread(target=self.update).start()
        
    def update(self):
        if self.port is not None:
            while True:
                try:
                    serialPort = None
                    while True:
                        try:
                            if serialPort is None:
                                serialPort = serial.Serial(self.port, baudrate=self.baudrate, timeout=5.0)
                            line = serialPort.readline().decode("utf-8")
                            self.parseGPS(line)
                        except:
                            serialPort = None
                            logging.error(sys.exc_info(), exc_info=True)
                            time.sleep(10)
                except:
                    logging.error(sys.exc_info(), exc_info=True)
                    time.sleep(10)
        else:
            longging.info("no port")
        
    def parseGPS(self, line):
        if line.find("GGA") > 0:
            self.position = pynmea2.parse(line)
            self.dataUpdated()
            
        if line.find("GPRMC") > 0:
            data = line.split(',')
            logging.debug(line + ":" + data[7])
            speedkmh = float(data[7]) * 1.852
            logging.debug("speed: " + str(speedkmh))
            if speedkmh < 1:
                speedkmh = 0
            self.speedkmh = speedkmh
            self.dataUpdated()
        
    def dataUpdated(self):
        if self.callbackAfterData is not None:
            self.callbackAfterData()
            
    def getPosition(self):
        return self.position
    
    def getSpeedKmh(self):
        return self.speedkmh
    
    def toJSON(self, prefix="gps"):
        json = ""
        prefixText = ""
        if prefix is not None:
            prefixText = prefix + "_"
        try:
            if self.position is not None:
                if self.position.latitude is not None:
                    json += "\"" + prefixText + "latitude\": {}".format(self.position.latitude) + ",\n"
                if self.position.longitude is not None:
                    json += "\"" + prefixText + "longitude\": {}".format(self.position.longitude) + ",\n"
                if self.position.altitude is not None:
                    json += "\"" + prefixText + "altitude\": {}".format(self.position.altitude) + ",\n"
            if self.speedkmh is not None:
                json += "\"" + prefixText + "speedkmh\": {}".format(self.speedkmh) + ",\n"

        except:
            logging.warning(sys.exc_info(), exc_info=True)
        return json
    
    def fromJSONConfig(self, config):
        try:
            if config is not None:
                if config.get("gps"):
                    gps = config["gps"]
                else:
                    gps = config
                if gps.get("serialPortName"):
                    self.port = gps["serialPortName"]
        except:
            logging.info(sys.exc_info(), exc_info=True)
