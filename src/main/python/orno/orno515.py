#!/usr/bin/env python3

import sys
sys.path.append('..')

import time
import logging
import minimalmodbus
import threading
# import atorlib
# import sensor


class Orno515Serial():
    voltage: float = None
    ampere: float = None
    power: float = None
    allPower: float = None
    
    jsonPrefix: str = None
    name: str = None
    id: str = None
    port: str = None
    verbose: bool = False
    
    callbackAfterData = None
    
    updatetimeS: int = 10
    
    instrument: minimalmodbus.Instrument = None
    
    readingStarted: bool = False
    lastUpdatetime = time.time()
    maxtime: int = 70  # seconds
    
    def __init__(self,
                 name=None,
                 id=None,
                 port=None,
                 jsonPrefix=None,
                 verbose=False,
                 jsonConfig=None,
                 callbackAfterData=None):
        self.name = name
        self.id = id;
        self.port = port
        self.verbose = verbose
        self.callbackAfterData = callbackAfterData
        self.jsonPrefix = jsonPrefix
        if jsonConfig:
            self.fromJSONConfig(jsonConfig)
            
    def connect(self):
        try:
            self.instrument = minimalmodbus.Instrument(self.port, 1)  # port name, slave address (in decimal)
            self.instrument.mode = minimalmodbus.MODE_RTU
            self.instrument.serial.baudrate = 9600
            self.instrument.serial.bytesize = 8
            self.instrument.serial.parity = minimalmodbus.serial.PARITY_EVEN
            self.instrument.serial.stopbits = 1
            self.instrument.serial.timeout = 3
            if self.verbose:
                logging.info("connected")
        except:
            logging.error(sys.exc_info(), exc_info=True)
        
    def disconnect(self):
        try:
            if self.instrument is not None:
                logging.info("disconnect from: {} {}".format(self.id, self.instrument))
                # self.instrument.close()
        except:
            logging.error(sys.exc_info(), exc_info=True)
        self.instrument = None
        
    def requestOnce(self):
        try:
            if self.instrument is None:
                self.connect()
            if self.instrument is not None:
                self.voltage = self.instrument.read_register(0x131, 2, 3, True)
                # self.ampere = self.instrument.read_register(0x0139, 3, 3, True)
                self.ampere = self.instrument.read_register(0x013A, 3, 3, True)
                # self.power = self.instrument.read_register(0x0140, 2, 3, True)
                self.power = self.instrument.read_register(0x0141, 3, 3, True)
                self.allPower = self.instrument.read_long(0xa000, 3, False, 0) / 100
                lastUpdatetime = time.time()
                if self.verbose:
                    logging.info("values: {} {}V {}A {}kW {}kW".format(self.id, self.voltage, self.ampere, self.power, self.allPower))
                if self.callbackAfterData is not None:
                    if self.verbose:
                        logging.info("callbackAfterData: {} {}".format(self.id, str(line)))
                    self.callbackAfterData()
            else:
                if self.verbose:
                    logging.info("no instrument: {}".format(self.id))
                time.sleep(self.updatetimeS)
        except:
            logging.error(sys.exc_info(), exc_info=True)
            self.disconnect()
            self.checkAgeOfValues()
            time.sleep(1)
            
    def requestAlways(self):
        while True:
            try:
                self.requestOnce()
            except:
                logging.error(sys.exc_info(), exc_info=True)
                time.sleep(1)
            time.sleep(10)
                        
    def startReading(self):
        if self.port:
            # start reading values
            if not self.readingStarted:
                self.readingStarted = True
                threading.Thread(target=self.requestAlways).start()
            else:
                logging.warn("already started {}".format(self.id))
        else:
            logging.warning("no port given")
    
    def checkAgeOfValues(self):
        if (time.time() - self.lastUpdatetime) > self.maxtime:
            logging.debug("reset values after time {} {}/{}".format(self.id, self.maxtime, (time.time() - self.lastUpdatetime)))
            self.resetValues()
            self.dataChanged()
            
    def dataChanged(self):
        self.lastUpdatetime = time.time()
        if self.callbackAfterData is not None:
            if self.verbose:
                logging.info("callbackAfterData")
            self.callbackAfterData()
            
    def setJsonPrefix(self, prefix):
        self.jsonPrefix = prefix
        
    def getVoltage(self):
        self.checkAgeOfValues()
        return self.voltage
    
    def getAmpere(self):
        self.checkAgeOfValues()
        return self.ampere
    
    def getPower(self):
        self.checkAgeOfValues()
        return self.power
    
    def getAllPower(self):
        self.checkAgeOfValues()
        return self.allPower
    
    def resetValues(self):
        self.voltage = None
        self.ampere = None
        self.power = None
        self.allPower = None
            
    def toJSON(self, prefix: str=None):
        json = ""
        prefixText = ""
        if prefix is not None:
            prefixText = prefix + "_"
        else:
            if self.jsonPrefix:
                prefixText = self.jsonPrefix + "_"
        try:
            if self.getVoltage():
                json += "\"" + prefixText + "voltage\": {}".format(self.voltage) + ",\n"
            if self.ampere is not None:
                json += "\"" + prefixText + "ampere\": {}".format(self.ampere) + ",\n"
            if self.power is not None:
                json += "\"" + prefixText + "power\": {}".format(self.power) + ",\n"
            if self.allPower is not None:
                json += "\"" + prefixText + "all_power\": {}".format(self.allPower) + ",\n"
        except:
            logging.warning(sys.exc_info(), exc_info=True)
        return json

    def fromJSONConfig(self, config):
        try:
            if config is not None:
                if config.get("orno"):
                    orno = config["orno"]
                else:
                    orno = config
                if orno.get("515"):
                    orno515 = orno["515"]
                else:
                    orno515 = orno
                if orno515.get("serialPortName"):
                    self.port = orno515["serialPortName"]
            if self.verbose:
                logging.info("port: {}".format(self.port))
        except:
            logging.info(sys.exc_info(), exc_info=True)


def main():
    try:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s')
        
        port = "/dev/ttyUSB1"
        port = '/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A10MMQNK-if00-port0'
        logging.info("connect to " + port)
        id = "TestOrno"
        orno = Orno515Serial(port=port, id=id, verbose=True)
        orno.startReading()
        while(True):
            time.sleep(10000)
    except:
        logging.error(sys.exc_info(), exc_info=True)


if __name__ == '__main__':
    main()
