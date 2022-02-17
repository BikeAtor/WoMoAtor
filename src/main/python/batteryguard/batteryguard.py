#!/usr/bin/env python3

import sys
import time
import bluepy.btle
import threading
import logging

import atorlib


class BatteryGuard(atorlib.BleBluepyBase):
    
    voltage = None
    requestCounter = 0

    def __init__(self,
                 mac=None,
                 name=None,
                 data=None,
                 verbose=False,
                 updatetimeS=1,
                 callbackAfterData=None,
                 disconnectAfterData=False):
        super().__init__(mac=mac, name=name, data=data, verbose=verbose,
               updatetimeS=updatetimeS,
               callbackAfterData=callbackAfterData, disconnectAfterData=disconnectAfterData)
        
    # send request to battery for Realtime-Data
    def requestData(self):
        # Characteristic <SC Control Point> uuid: 00002a55-0000-1000-8000-00805f9b34fb handle: 47 properties: NOTIFY
        # Characteristic <RSC Measurement> uuid: 00002a53-0000-1000-8000-00805f9b34fb handle: 37 properties: NOTIFY
        try:
            # every time notification is turned on we will get another value.so reset from time to time
            self.requestCounter += 1
            if self.requestCounter % 5 == 0:
                self.disconnect()
                self.connect()
            handle = 37
            # enable notify
            self.peripheral.writeCharacteristic(handle + 1, b"\x01\x00")
        except:
            logging.error(sys.exc_info(), exc_info=True)
    
    def floatValue(self, nums):
        # check if value is negative
        num = (nums[1] << 8) | nums[0]
        if nums[1] == 0xff:
            num = -((num ^ 0xffff) + 1)
        return num

    # try to read values from data
    def parseData(self, data):
        if self.verbose:
            logging.debug("parseData: " + str(data))
        try:
            if data is not None:
                if self.verbose:
                    logging.debug("length: " + str(len(data)))
                if len(data) >= 3:
                    value = self.floatValue(data[1:3])
                    if self.verbose:
                        logging.info("data: {}" .format(value))
                    self.voltage = value / 1000.0
                    self.dataChanged()
        except:
            logging.error(sys.exc_info(), exc_info=True)
            
    def resetValues(self):
        self.voltage = None
        
    def getVoltage(self):
        self.checkAgeOfValues()
        return self.voltage
    
    def toJSON(self, prefix="battery"):
        json = ""
        prefixText = ""
        if prefix is not None:
            prefixText = prefix + "_"
        try:
            if self.getVoltage() is not None:
                json += "\"" + prefixText + "voltage\": {}".format(self.getVoltage()) + ",\n"

        except:
            logging.warning(sys.exc_info(), exc_info=True)
        return json


def main():
    try:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s')
        
        mac = "c8:fd:19:41:29:6b"
        logging.info("connect to " + mac)
        gas = BatteryGuard(mac=mac, verbose=True, updatetimeS=10, disconnectAfterData=False)
        gas.startReading()
        while(True):
            time.sleep(10000)
    except:
        logging.error(sys.exc_info(), exc_info=True)


if __name__ == '__main__':
    main()
