#!/usr/bin/env python3

import sys
from abc import abstractmethod
import time
import threading
import logging
import serial
from cffi.pkgconfig import call


# read data from serial interface
class SerialBase():
    verbose = False
    port = None
    id = None
    ports = {"/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyUSB2", "/dev/ttyUSB3", "/dev/ttyUSB4", "/dev/ttyUSB5", "/dev/ttyUSB6"}
    serial = None
    name = None
    mtuSize = None
    baudrate = 115200
    timeout = 20
    disconnectAfterData = False;
    callbackAfterData = None
    jsonPrefix = None
    
    lastUpdatetime = time.time()
    maxtime = 70  # seconds
    
    def __init__(self,
                 port=None,
                 id=None,
                 baudrate=None,
                 name=None,
                 jsonPrefix=None,
                 data=None,
                 verbose=False,
                 callbackAfterData=None,
                 maxtime=120):
        self.verbose = verbose
        self.port = port
        self.id = id
        self.name = name
        if self.name is None:
            self.name = "noname"
        self.jsonPrefix = jsonPrefix
        if baudrate is not None:
            self.baudrate = baudrate
        self.maxtime = maxtime
        self.callbackAfterData = callbackAfterData
        if data is not None:
            self.parseData(data)
        if self.port is None and self.id is not None:
            self.port = self.findPortByID() 
   
    # try to read values from data
    @abstractmethod
    def parseData(self, data):
        raise NotImplementedError()
    
    @abstractmethod
    def resetValues(self):
        raise NotImplementedError()
    
    def setName(self, name):
        self.name = name
        if self.name is None:
            self.name = "noname"
    
    def setId(self, id):
        self.id = id
        if self.id:
            self.port = self.findPortByID()
            
    def setJsonPrefix(self, prefix):
        self.jsonPrefix = prefix
        
    def setCallbackAfterData(self, callback):
        self.callbackAfterData = callback
        
    def dataChanged(self):
        self.lastUpdatetime = time.time()
        if self.callbackAfterData is not None:
            if self.verbose:
                logging.info("callbackAfterData")
            self.callbackAfterData()
    
    def checkAgeOfValues(self):
        if (time.time() - self.lastUpdatetime) > self.maxtime:
            logging.debug("reset values after time {}/{}".format(self.maxtime, (time.time() - self.lastUpdatetime)))
            self.resetValues()
            self.dataChanged()
        
    def startReading(self):
        if self.port is not None:
            # start reading values
            threading.Thread(target=self.requestAlways).start()
        else:
            logging.warning("no port given")
            
    def connect(self):
        try:
            if self.port is not None:
                if self.verbose:
                    logging.info("connect to: {}".format(self.port))
                self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            else:
                logging.info("no port")
        except:
            self.disconnect()
            self.checkAgeOfValues()
            logging.error(sys.exc_info())
            # logging.error(sys.exc_info(), exc_info=True)
            
    def disconnect(self):
        try:
            if self.serial is not None:
                logging.info("disconnect from: {}".format(self.serial))
                self.serial.close()
        except:
            logging.error(sys.exc_info(), exc_info=True)
        self.serial = None
        
    # set data
    def setData(self, data):
        self.parseData(data)
            
    def requestAlways(self):
        while True:
            try:
                self.requestOnce()
            except:
                logging.error(sys.exc_info(), exc_info=True)
                time.sleep(1)
                
    def requestOnce(self):
        try:
            if self.serial is None:
                self.connect()
            if self.serial is not None:
                
                if self.verbose:
                    logging.info("wait for data")
                lineRaw = self.serial.readline()
                values = bytearray(lineRaw)
                for x in range(len(values)):
                    if values[x] > 127:
                        values[x] = 32
                line = values.decode("ASCII")
                # remove newline at end
                line = line.rstrip()
                self.parseData(line)
                if self.callbackAfterData is not None:
                    if self.verbose:
                        logging.info("callbackAfterData: " + str(line))
                    self.callbackAfterData()
            else:
                if self.verbose:
                    logging.info("no serial")
                time.sleep(self.updatetimeS)
        except:
            logging.error(sys.exc_info(), exc_info=True)
            self.disconnect()
            self.checkAgeOfValues()
            time.sleep(1)
    
    def findPortByID(self):
        if self.id is None:
            return None
        for p in self.ports:
            # if self.verbose:
            logging.info("try port: {}".format(p))
            s = None
            try:
                s = serial.Serial(p, self.baudrate, timeout=2, inter_byte_timeout=2)
                
                # try to read 20 lines
                for i in range(20):
                    logging.info("try: {}".format(i))
                    line = None
                    if True:
                        line = self.readline(s, 4)
                    else:
                        lineRaw = s.readline()
                        values = bytearray(lineRaw)
                        for x in range(len(values)):
                            if values[x] > 127:
                                values[x] = 32
                        line = values.decode("ASCII")
                    if line:
                        # remove newline at end
                        line = line.rstrip()
                        if self.verbose:
                            logging.debug("line: {} {}".format(p, line))
                        if len(line) == 0:
                            logging.info("empty line: {}".format(p))
                            break
                        if line == "ID: " + self.id:
                            logging.info("found: {} {}".format(p, line))
                            return p
                        if line.startswith("ID: "):
                            logging.info("wrong ID: {}".format(self.id))
                            break;
                    else:
                        logging.info("no line: {}".format(p))
                        break

            except:
                logging.error(sys.exc_info(), exc_info=False)
            finally:
                try:
                    if s:
                        logging.info("close: {}".format(p))
                        s.close()
                except:
                    logging.error(sys.exc_info(), exc_info=False)   
        return None
    
    def readline(self, serial, timeout):
        tic = time.time()
        buff = ""
        found = False
        while (time.time() - tic) < timeout and not found:
            bytes = serial.read()
            if bytes and len(bytes) > 0:
                for b in bytes:
                    if b == 10 or b == 13:
                        found = True
                        break;
                    if b > 127:
                        buff += " "
                    else:
                        buff += chr(b)
                    
        if not found:
            # logging.info("no data received")
            return None
        # logging.info("buff: {}".format(buff))
        if len(buff) == 0:
            # empty line, so try to get another (maybe \n\r)
            return self.readline(serial, timeout)
        return buff
        
    def toJSON(self, prefix=None):
        return ""
