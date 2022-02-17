#!/usr/bin/env python3

import sys
sys.path.append('..')

import time
import logging

import atorlib
import ble_temperature_sensor


class AzartonSensor(atorlib.BleBluepyBase):
    
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
        # Characteristic <ebe0ccd9-7a0a-4b0c-8a1a-6ff2997da3a6> uuid: ebe0ccd9-7a0a-4b0c-8a1a-6ff2997da3a6 handle: 76 properties: WRITE NOTIFY 
        try:
            if self.peripheral is not None:
                if False:
                    handle = 3
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
                if len(data) >= 2:
                    value = self.floatValue(data[0:2])
                    if self.verbose:
                        logging.debug("temp: {}" .format(value))
                    self.sensor.temperature = value / 100.0
                    
                if len(data) >= 3:
                    value = int(self.data[2])
                    if self.verbose:
                        logging.debug("hum: {}" .format(value))
                    self.sensor.humidity = value
                    
                if len(data) >= 4:
                    value = int(self.data[3])
                    if self.verbose:
                        logging.debug("bat: {}" .format(value))
                    self.sensor.battery = value
                    
                if found:
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
        print("start azartorsensor")
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s')
        logging.getLogger().setLevel(logging.DEBUG)
        
        mac = "A4:C1:38:DF:CB:2C"
        logging.debug("connect to: " + mac)
        sensor = AzartonSensor(mac=mac, name="ArzatonTest", verbose=True, updatetimeS=10, disconnectAfterData=True)
        sensor.startReading()
        while(True):
            time.sleep(10000)
    except:
        logging.error(sys.exc_info(), exc_info=True)


if __name__ == '__main__':
    main()
