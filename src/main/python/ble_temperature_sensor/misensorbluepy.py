#!/usr/bin/env python3

import sys
sys.path.append('..')
sys.path.append('/home/pi/python/mitemp')

import logging
import threading
import time

import atorlib
import ble_temperature_sensor
# bluetooth
from mitemp_bt.mitemp_bt_poller import MiTempBtPoller, MI_TEMPERATURE, MI_HUMIDITY, MI_BATTERY
# GUI
import tkinter as tk
import tkinter.font as tkFont


class MiSensorBluepy(atorlib.BleBluepyBase):
    
    sensor = None

    def __init__(self,
                 mac=None,
                 name=None,
                 data=None,
                 verbose=False,
                 updatetimeS=1,
                 callbackAfterData=None,
                 disconnectAfterData=False):
        super().__init__(mac=mac, name=name, data=data, verbose=verbose,
               updatetimeS=updatetimeS, callbackAfterData=callbackAfterData, disconnectAfterData=disconnectAfterData)
        self.sensor = ble_temperature_sensor.Sensor(name=self.name, address=mac,
                                                    type=ble_temperature_sensor.SensorType.AZARTON
                                                    )
        if self.verbose:
            logging.info("init finished")

    # send request to battery for Realtime-Data
    def requestData(self):
        try:
            if self.peripheral is not None:
                if True:
                    handle = 0x000f
                    # enable notify
                    self.peripheral.writeCharacteristic(handle + 1, b"\x01\x00")
                    if self.verbose:
                        logging.info("notification send to handle {}".format(handle))
                if True and self.peripheral is not None:
                    # Characteristic <Device Name> uuid: 00002a00-0000-1000-8000-00805f9b34fb handle: 3 properties: READ NOTIFY
                    handle = 3
                    msg = self.peripheral.readCharacteristic(handle)
                    if self.verbose:
                        logging.info("read from handle {} {}".format(handle, msg))
            else:
                logging.warning("no peripheral")
        except:
            logging.error(sys.exc_info(), exc_info=True)
            self.disconnect()
    
    def floatValue(self, nums):
        # check if value is negative
        num = (nums[1] << 8) | nums[0]
        if nums[1] == 0xff:
            num = -((num ^ 0xffff) + 1)
        return num

    # try to read values from data
    def parseData(self, data):
        if self.verbose:
            logging.info("parseData: " + str(data))
        try:
            if data is not None:
                if self.verbose:
                    logging.debug("length: " + str(len(data)))
                
                found = False
                if len(data) >= 6:
                    # T=6.1 H=75.5
                    text = ""
                    for i in range(len(data)):
                        # 0-9:
                        if data[i] >= 48 and data[i] <= 57:
                            text += data[i:i + 1].decode("ASCII")
                        # . =
                        if data[i] == 46 or data[i] == 32 or data[i] == 61:
                            text += data[i:i + 1].decode("ASCII")
                        # A-Z
                        if data[i] >= 65 and data[i] <= 90:
                            text += data[i:i + 1].decode("ASCII")
                            
                    # text = str(data)
                    # text = text.strip('\\x00')
                    if self.verbose:
                        logging.info("text: {}".format(text))
                    for dataitem in text.split(' '):
                        dataparts = dataitem.split('=')
                        if dataparts[0] == 'T':
                            self.sensor.temperature = float(dataparts[1])
                            found = True
                        elif dataparts[0] == 'H':
                            self.sensor.humidity = float(dataparts[1])
                            found = True
                if found:
                    if self.verbose:
                        logging.info("{}°C {}%".format(self.sensor.temperature, self.sensor.humidity)) 
                    self.dataChanged()
        except:
            logging.error(sys.exc_info(), exc_info=True)
            
    def resetValues(self):
        self.sensor.resetValues()
        
    def getTemperature(self):
        self.checkAgeOfValues()
        return self.sensor.temperature
    
    def getSensor(self):
        return self.sensor
    
    def toJSON(self, prefix="sensor"):
        return self.sensor.toJSON(prefix=prefix)


def main():
    try:
        print("start misensor")
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s')
        logging.getLogger().setLevel(logging.DEBUG)
        
        # mac = "58:2d:34:39:17:d2"
        # georg
        mac = "58:2d:34:39:1a:c2"
        logging.debug("connect to: " + mac)
        sensor = MiSensor(mac=mac, name="MiTest", verbose=True, updatetimeS=10, disconnectAfterData=True)
        sensor.startReading()
        while(True):
            time.sleep(10000)
    except:
        logging.error(sys.exc_info(), exc_info=True)


if __name__ == '__main__':
    main()

