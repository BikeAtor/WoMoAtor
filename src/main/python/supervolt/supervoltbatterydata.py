#!/usr/bin/env python3

'''
connect to: 84:28:D7:8F:54:70
notificationhandler installed
services: 
Service <uuid=Generic Attribute handleStart=1 handleEnd=4>
Service <uuid=Generic Access handleStart=5 handleEnd=13>
Service <uuid=6e400001-b5a3-f393-e0a9-e50e24dcca9e handleStart=14 handleEnd=65535>

characteristics: 
Characteristic <Service Changed> uuid: 00002a05-0000-1000-8000-00805f9b34fb handle: 3 properties: INDICATE 
indicate enabled: 4
Characteristic <Device Name> uuid: 00002a00-0000-1000-8000-00805f9b34fb handle: 7 properties: READ 
length: 7 value: b'libatt\x00'
Characteristic <Appearance> uuid: 00002a01-0000-1000-8000-00805f9b34fb handle: 9 properties: READ 
length: 2 value: b'\x00\x00'
Characteristic <Peripheral Preferred Connection Parameters> uuid: 00002a04-0000-1000-8000-00805f9b34fb handle: 11 properties: READ 
length: 8 value: b'\x00\x00\x00\x00\x00\x00\x00\x00'
Characteristic <Central Address Resolution> uuid: 00002aa6-0000-1000-8000-00805f9b34fb handle: 13 properties: READ 
length: 1 value: b'\x00'
Characteristic <0002> uuid: 00000002-0000-1000-8000-00805f9b34fb handle: 16 properties: READ 
length: 2 value: b'\x01\x02'
Characteristic <6e400002-b5a3-f393-e0a9-e50e24dcca9e> uuid: 6e400002-b5a3-f393-e0a9-e50e24dcca9e handle: 19 properties: WRITE NO RESPONSE WRITE 
Characteristic <6e400003-b5a3-f393-e0a9-e50e24dcca9e> uuid: 6e400003-b5a3-f393-e0a9-e50e24dcca9e handle: 21 properties: NOTIFY 
send notify: desc: [<bluepy.btle.Descriptor object at 0xb655ae30>] handle[0]: 22
Characteristic <0001> uuid: 00000001-0000-1000-8000-00805f9b34fb handle: 24 properties: INDICATE 
indicate enabled: 25
'''
import sys
sys.path.append('..')
import os
os.environ['PATH'] = 'C:/msys64/mingw64/bin' + os.pathsep + os.environ['PATH']
import time
import atorlib
import threading
import logging


# read data from notification
class SupervoltBatteryData():

    cellV = None
    totalV = None
    soc = None
    workingState = None
    alarm = None
    chargingA = None;
    dischargingA = None
    loadA = None
    tempC = None
    completeAh = None
    remainingAh = None
    designedAh = None
    verbose: bool = False
    
    updatetimeS: int = 10
    lastUpdatetime: float = time.time()
    maxtime: float = 70  # seconds
    
    def __init__(self,
                 updatetimeS=10,
                 verbose=False,
                 ):
        self.tempC = [None, None, None, None]
        self.cellV = [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
        self.updatetimeS = updatetimeS
        self.maxtime = self.updatetimeS * 10
            
    def setData(self, data):
        if data:
            self.parseData(data)
        
    # try to read values from data
    def parseData(self, data):
        if self.verbose:
            logging.debug("parseData: {}".format(len(data)))
        try:
            if data:
                if len(data) == 128:
                    if self.verbose:
                        logging.info("parse Realtimedata: {}".format(type(data)))
                    if type(data) is bytearray: 
                        data = bytes(data)
                    if type(data) is bytes:
                        # print("bytes")
                    
                        start = 1
                        end = start + 2
                        self.address = int(data[start: end].decode(), 16)
                        if self.verbose:
                            logging.debug("address: " + str(self.address))
                        
                        start = end
                        end = start + 2
                        self.command = int(data[start: end].decode(), 16)
                        if self.verbose:
                            logging.debug("command: " + str(self.command))
                        
                        start = end
                        end = start + 2
                        self.version = int(data[start: end].decode(), 16)
                        if self.verbose:
                            logging.debug("version: " + str(self.version))
                        
                        start = end
                        end = start + 4
                        self.length = int(data[start: end].decode(), 16)
                        if self.verbose:
                            logging.debug("length: " + str(self.length))
                        
                        start = end
                        end = start + 14
                        bdate = data[start: end]
                        if self.verbose:
                            logging.debug("date: " + str(bdate))
                    
                        start = end
                        end = start + 16 * 4
                        bvoltarray = data[start: end]
                        # print("voltarray: " + str(bvoltarray))
                        self.totalV = 0
                        if self.cellV:
                            for i in range(0, 11):
                                bvolt = data[(start + i * 4): (start + i * 4 + 4)]
                                self.cellV[i] = int(bvolt.decode(), 16) / 1000.0
                                self.totalV += self.cellV[i]
                                if self.verbose:
                                    logging.debug("volt" + str(i) + ": " + str(bvolt) + " / " + str(self.cellV[i]) + "V")
                        
                        if self.verbose:
                            logging.debug("totalVolt: " + str(self.totalV))
                        
                        start = end
                        end = start + 4
                        bcharging = data[start: end]
                        self.chargingA = int(bcharging.decode(), 16) / 100.0
                        if self.verbose:
                            logging.debug("charching: " + str(bcharging) + " / " + str(self.chargingA) + "A")
                        if self.chargingA > 500:
                            # problem with supervolt
                            logging.info("charging too big: {}".format(self.chargingA))
                            self.chargingA = 0.0
                            
                        start = end
                        end = start + 4
                        bdischarging = data[start: end]
                        self.dischargingA = int(bdischarging.decode(), 16) / 100.0
                        if self.verbose:
                            logging.debug("discharching: " + str(bdischarging) + " / " + str(self.dischargingA) + "A")
                        if self.dischargingA > 500:
                            # problem with supervolt
                            logging.info("discharging too big: {}".format(self.dischargingA))
                            self.dischargingA = 0.0
                        
                        self.loadA = -self.chargingA + self.dischargingA
                        
                        for i in range(0, 4):
                            start = end
                            end = start + 2
                            if self.tempC:
                                btemp = data[start: end]
                                self.tempC[i] = int(btemp.decode(), 16) - 40
                                if self.verbose:
                                    logging.debug("temp" + str(i) + ": " + str(btemp) + " / " + str(self.tempC[i]) + "°C")
                        
                        start = end
                        end = start + 4
                        self.workingState = int(data[start: end].decode(), 16)
                        if self.verbose:
                            logging.debug("workingstate: " + str(self.workingState) + " / " + str(data[start: end])
                              +" / " + self.getWorkingStateTextShort() + " / " + self.getWorkingStateText())
                        
                        start = end
                        end = start + 2
                        self.alarm = int(data[start: end].decode(), 16)
                        if self.verbose:
                            logging.debug("alarm: " + str(self.alarm))
                        
                        start = end
                        end = start + 4
                        self.balanceState = int(data[start: end].decode(), 16)
                        if self.verbose:
                            logging.debug("balanceState: " + str(self.balanceState))
                        
                        start = end
                        end = start + 4
                        self.dischargeNumber = int(data[start: end].decode(), 16)
                        if self.verbose:
                            logging.debug("dischargeNumber: " + str(self.dischargeNumber))
                            
                        start = end
                        end = start + 4
                        self.chargeNumber = int(data[start: end].decode(), 16)
                        if self.verbose:
                            logging.debug("chargeNumber: " + str(self.chargeNumber))
                        
                        # State of Charge (%)
                        start = end
                        end = start + 2
                        self.soc = int(data[start: end].decode(), 16)
                        if self.verbose:
                            logging.debug("soc: " + str(self.soc))
                            logging.info("end of parse realtimedata")
                    else:
                        logging.warning("no bytes")
                elif len(data) == 30:
                    if self.verbose:
                        logging.debug("capacity")
                    if type(data) is bytearray: 
                        data = bytes(data)
                    if type(data) is bytes:
                        start = 1
                        end = start + 2
                        self.address = int(data[start: end].decode(), 16)
                        if self.verbose:
                            logging.debug("address: " + str(self.address))
                        
                        start = end
                        end = start + 2
                        self.command = int(data[start: end].decode(), 16)
                        if self.verbose:
                            logging.debug("command: " + str(self.command))
                        
                        start = end
                        end = start + 2
                        self.version = int(data[start: end].decode(), 16)
                        if self.verbose:
                            logging.debug("version: " + str(self.version))
                        
                        start = end
                        end = start + 4
                        self.length = int(data[start: end].decode(), 16)
                        if self.verbose:
                            logging.debug("length: " + str(self.length))
                        
                        start = end
                        end = start + 4
                        breseved = data[start: end]
                        if self.verbose:
                            logging.debug("reseved: " + str(breseved))
                        
                        start = end
                        end = start + 4
                        self.remainingAh = int(data[start: end].decode(), 16) / 10.0
                        if self.verbose:
                            logging.debug("remainingAh: " + str(self.remainingAh) + " / " + str(data[start: end]))
                        
                        start = end
                        end = start + 4
                        self.completeAh = int(data[start: end].decode(), 16) / 10.0
                        if self.verbose:
                            logging.debug("completeAh: " + str(self.completeAh))
                        
                        start = end
                        end = start + 4
                        self.designedAh = int(data[start: end].decode(), 16) / 10.0
                        if self.verbose:
                            logging.debug("designedAh: " + str(self.designedAh))
                            logging.info("end of parse capacity")
                        
                else:
                    logging.warning("wrong length: " + str(len(data)))
            else:
                logging.debug("no data")
        except:
            logging.error(sys.exc_info(), exc_info=True)
       
    def resetValues(self):
        try:
            logging.info("reset")
            self.alarm = None
            self.balanceState = None
            if self.cellV:
                for i in range(0, 11):
                    self.cellV[i] = None
            self.chargeNumber = None
            self.chargingA = None
            self.completeAh = None
            self.designedAh = None
            self.dischargeNumber = None
            self.dischargingA = None
            self.loadA = None
            self.remainingAh = None
            self.soc = None
            if self.tempC:
                for i in range(0, 4):
                    self.tempC[i] = None
            self.totalV = None
            self.version = None
            self.workingState = None
        except:
            logging.error(sys.exc_info(), exc_info=True)
    
    def getWorkingStateTextShort(self):
        if self.workingState is None:
            return "nicht erreichbar"
        if self.workingState & 0xF003 >= 0xF000:
            return "Normal"
        if self.workingState & 0x000C > 0x0000:
            return "Schutzschaltung"
        if self.workingState & 0x0020 > 0:
            return "Kurzschluss"
        if self.workingState & 0x0500 > 0:
            return "Überhitzt"
        if self.workingState & 0x0A00 > 0:
            return "Unterkühlt"
        return "Unbekannt"
        
    def getWorkingStateText(self):
        text = ""
        if self.workingState is None:
            return "Unbekannt"
        if self.workingState & 0x0001 > 0:
            text = self.appendState(text, "Laden")
        if self.workingState & 0x0002 > 0:
            text = self.appendState(text , "Entladen")
        if self.workingState & 0x0004 > 0:
            text = self.appendState(text , "Überladungsschutz")
        if self.workingState & 0x0008 > 0:
            text = self.appendState(text , "Entladeschutz")
        if self.workingState & 0x0010 > 0:
            text = self.appendState(text , "Überladen")
        if self.workingState & 0x0020 > 0:
            text = self.appendState(text , "Kurzschluss")
        if self.workingState & 0x0040 > 0:
            text = self.appendState(text , "Entladeschutz 1")
        if self.workingState & 0x0080 > 0:
            text = self.appendState(text , "Entladeschutz 2")
        if self.workingState & 0x0100 > 0:
            text = self.appendState(text , "Überhitzt (Laden)")
        if self.workingState & 0x0200 > 0:
            text = self.appendState(text , "Unterkühlt (Laden)")
        if self.workingState & 0x0400 > 0:
            text = self.appendState(text , "Überhitzt (Entladen)")
        if self.workingState & 0x0800 > 0:
            text = self.appendState(text , "Unterkühlt (Entladen)")
        if self.workingState & 0x1000 > 0:
            text = self.appendState(text , "DFET an")
        if self.workingState & 0x2000 > 0:
            text = self.appendState(text , "CFET an")
        if self.workingState & 0x4000 > 0:
            text = self.appendState(text , "DFET Schalter an")
        if self.workingState & 0x8000 > 0:
            text = self.appendState(text , "CFET Schalter an")
        
        return text

    def appendState(self, text, append):
        if text is None  or len(text) == 0:
            return append
        return text + " | " + append
    
    def checkAgeOfValues(self) -> bool:
        if (time.time() - self.lastUpdatetime) > self.maxtime:
            # data is old
            return False
        #    if (time.time() - self.lastResettime) > self.maxtime:
        #        # last time for reset is also too old, so it will be called every maxtime
        #        self.lastResettime = time.time()
        #        logging.debug("reset values after time {}/{}".format(self.maxtime, (time.time() - self.lastUpdatetime)))
        #        self.resetValues()
        #        self.dataChanged(False)
        return True
    
    def toJSON(self, prefix: str="battery") -> str:
        if self.checkAgeOfValues():
            json = ""
            prefixText = ""
            if prefix is not None:
                prefixText = prefix + "_"
            try:
                if self.tempC:
                    if self.tempC[0] is not None:
                        json += "\"" + prefixText + "temperature\": {}".format(self.tempC[0]) + ",\n"
                if self.totalV is not None:
                    json += "\"" + prefixText + "voltage\": {}".format(self.totalV) + ",\n"
                if self.cellV:
                    if self.cellV[0] is not None:
                        json += "\"" + prefixText + "voltage_cell0\": {}".format(self.cellV[0]) + ",\n"
                    if self.cellV[1] is not None:
                        json += "\"" + prefixText + "voltage_cell1\": {}".format(self.cellV[1]) + ",\n"
                    if self.cellV[2] is not None:
                        json += "\"" + prefixText + "voltage_cell2\": {}".format(self.cellV[2]) + ",\n"
                    if self.cellV[3] is not None:
                        json += "\"" + prefixText + "voltage_cell3\": {}".format(self.cellV[3]) + ",\n"
                if self.soc is not None:
                    json += "\"" + prefixText + "soc\": {}".format(self.soc) + ",\n"
                if self.chargingA is not None:
                    json += "\"" + prefixText + "chargingA\": {}".format(self.chargingA) + ",\n"
                if self.dischargingA is not None:
                    json += "\"" + prefixText + "dischargingA\": {}".format(self.dischargingA) + ",\n"
                if self.loadA is not None:
                    json += "\"" + prefixText + "loadA\": {}".format(self.loadA) + ",\n"
                if self.alarm is not None:
                    json += "\"" + prefixText + "alarm\": {}".format(self.alarm) + ",\n"
                if self.workingState is not None:
                    json += "\"" + prefixText + "workingState\": {}".format(self.workingState) + ",\n"
                    withoutUmlaute = self.getWorkingStateText().replace("Ü", "Ue").replace("ü", "ue")
                    json += "\"" + prefixText + "workingStateText\": \"{}\"".format(withoutUmlaute) + ",\n"
                    withoutUmlaute = self.getWorkingStateTextShort().replace("Ü", "Ue").replace("ü", "ue")
                    json += "\"" + prefixText + "workingStateTextShort\": \"{}\"".format(withoutUmlaute) + ",\n"
                if self.completeAh is not None:
                    json += "\"" + prefixText + "completeAh\": {}".format(self.completeAh) + ",\n"
                if self.remainingAh is not None:
                    json += "\"" + prefixText + "remainingAh\": {}".format(self.remainingAh) + ",\n"
                if self.designedAh is not None:
                    json += "\"" + prefixText + "designedAh\": {}".format(self.designedAh) + ",\n"

            except:
                logging.warning(sys.exc_info(), exc_info=True)
            return json
        else:
            # too old
            return ""
        
    def getLastUpdateTime(self) -> float:
        return self.lastUpdatetime
