#!/usr/bin/env python3

import sys
from numpy.core import _string_helpers
import string
sys.path.append('..')
sys.path.append('lib')

import logging
import ble_temperature_sensor
from abc import abstractmethod
import struct
import sensor


class Sensor(sensor.Sensor):
    name: string = None
    id: string = None
    address: string = None
    type: ble_temperature_sensor.SensorType = None
    temperature: float = None
    humidity: float = None
    battery: float = None
    callbackAfterData = None
    verbose: bool = False
    jsonPrefix: string = None
    
    def __init__(self, name=None, address=None,
                 type=ble_temperature_sensor.SensorType.UNKNOWN, callbackAfterData=None,
                 verbose=False):
        self.name = name
        callbackAfterData = callbackAfterData
        if address is not None:
            self.address = address.lower()
        self.type = type
        self.verbose = verbose
        
    @abstractmethod
    def parseData(self, data):
        return False
    
    def setId(self, id: string):
        self.id = id
        
    def setName(self, name: string):
        self.name = name
        
    def setMac(self, mac: string):
        self.address = mac.lower()
    
    def setJsonPrefix(self, prefix: string):
        self.jsonPrefix = prefix
        
    def setVerbose(self, verbose: string):
        if verbose:
            self.verbose = prefix.upper() == "TRUE"
            
    def getBatteryLevel(self) -> float:
        return self.battery;
    
    def getTemperature(self) -> float:
        return self.temperature;
    
    def getHumidity(self) -> float:
        return self.humidity;

    def resetValues(self):
        self.temperature = None
        self.humidity = None
        self.battery = None
        
    def toJSON(self, prefix="sensor"):
        json = ""
        prefixText = ""
        if prefix:
            prefixText = prefix + "_"
        elif self.jsonPrefix:
            prefixText = self.jsonPrefix + "_"
        try:
            if self.temperature is not None:
                json += "\"" + prefixText + "temperature\": {}".format(self.temperature) + ",\n"
            if self.humidity is not None:
                json += "\"" + prefixText + "humidity\": {}".format(self.humidity) + ",\n"
            if self.battery is not None:
                json += "\"" + prefixText + "battery\": {}".format(self.battery) + ",\n"

        except:
            logging.warning(sys.exc_info(), exc_info=True)
        return json
    
    def twosComplement(self, n: int, w: int=16) -> float:
        """Two's complement integer conversion."""
        # Adapted from: https://stackoverflow.com/a/33716541.
        if n & (1 << (w - 1)):
            n = n - (1 << w)
        return n / 100.0
    
    def floatValue(self, nums):
        # check if value is negative
        num = (nums[1] << 8) | nums[0]
        if nums[1] == 0xff:
            num = -((num ^ 0xffff) + 1)
        return float(num)
    
    def floatValue100(self, nums):
        return self.floatValue(nums) / 100.0

    
class SensorGovee(Sensor):
    
    def __init__(self, name=None, address=None, callbackAfterData=None, verbose=False):
        super().__init__(name=name, address=address, callbackAfterData=callbackAfterData,
                         verbose=verbose,
                         type=ble_temperature_sensor.SensorType.GOVEE)
        
    def parseData(self, data):
        try:
            if len(data) >= 11:
                temp, hum, batt = struct.unpack_from("<HHB", data, 6)
                if self.verbose:
                    logging.info("govee {} {} {} {} {} {}".format(self.name,
                                                                self.floatValue(data[0:2]) / 100,
                                                                self.twosComplement(temp),
                                                                hum / 100.0,
                                                                batt,
                                                                data.hex()))
                self.temperature = float(self.twosComplement(temp))
                # sensor.temperature = self.floatValue100(advertisement.mfg_data[0:2]) / 100.0
                self.humidity = float(hum / 100.0)
                self.battery = batt
                self.updateGUISensor(sensor)
                return True
            else:
                if self.verbose:
                    logging.info("govee wrong length: {} {}".format(len(data), data.hex()))
        except:
            logging.warning(sys.exc_info(), exc_info=True)
        return False

    
class SensorInkbird(Sensor):
    
    def __init__(self, name=None, address=None, callbackAfterData=None, verbose=False):
        super().__init__(name=name, address=address, callbackAfterData=callbackAfterData,
                         verbose=verbose,
                         type=ble_temperature_sensor.SensorType.INKBIRD)
        
    def parseData(self, data):
        try:
            if len(data) >= 7:
                # temp = self.floatValue100(advertisement.mfg_data[0:2])
                temp = float(int.from_bytes(data[0:2], byteorder='little', signed=True) / 100.0)
                hum = self.floatValue100(data[2:4])
                # bat = self.floatValue100(data[4:6])
                bat = data[7]
                if self.verbose:
                    logging.info("inkbird {} {:.1f}° {:.0f}% {} {}".format(self.name, temp, hum, bat, data.hex()))
                self.temperature = float(temp)
                self.humidity = float(hum)
                self.battery = float(bat)
                # TODO battery
                return True
            else:
                if self.verbose:
                    logging.info("inkbird wrong length: {} {}".format(len(data), data.hex()))
        except:
            logging.warning(sys.exc_info(), exc_info=True)
        return False

    
class SensorBrifit(Sensor):
    
    def __init__(self, name=None, address=None, callbackAfterData=None, verbose=False):
        super().__init__(name=name, address=address, callbackAfterData=callbackAfterData,
                         verbose=verbose,
                         type=ble_temperature_sensor.SensorType.BRIFIT)
        
    def parseData(self, data):
        try:
            if len(data) == 20:  # bluepy
                batt, temp, hum = struct.unpack('<BhH', data[11:16])
                if self.verbose:
                    logging.info("brifit {} {:.1f}° {:.0f}% {} {}".format(self.name,
                                                                          temp / 16.0,
                                                                          hum / 16.0,
                                                                          batt / 16.0 * 100,
                                                                          data.hex()))
                self.temperature = float(temp / 16.0)
                self.humidity = float(hum / 16.0)
                self.battery = float(batt / 16.0 * 100)
                # self.battery = float(data[11] / 16.0 * 10)
                return True
            elif len(data) == 18:  # bleak
                batt, temp, hum = struct.unpack('<BhH', data[9:14])
                if self.verbose:
                    # logging.info("data: {}".format(data.hex()))
                    logging.info("brifit {} {:.1f}° {:.0f}% {} {}".format(self.name,
                                                                          temp / 16.0,
                                                                          hum / 16.0,
                                                                          batt / 16.0 * 100,
                                                                          data.hex()))
                self.temperature = float(temp / 16.0)
                self.humidity = float(hum / 16.0)
                self.battery = float(batt / 16.0 * 100)
                # self.battery = float(data[11] / 16.0 * 10)
                return True
            else:
                if self.verbose:
                    logging.info("brifit wrong length: {} {}".format(len(data), data.hex()))
        except:
            logging.warning(sys.exc_info(), exc_info=True)
        return False


class SensorAzarton(Sensor):
    
    def __init__(self, name=None, address=None, callbackAfterData=None, verbose=False):
        super().__init__(name=name, address=address, callbackAfterData=callbackAfterData,
                         verbose=verbose,
                         type=ble_temperature_sensor.SensorType.AZARTON)
        
    def parseData(self, data):
        try:
            if self.verbose:
                logging.info("brifit data: {} {}".format(len(data), data.hex()))
            if len(data) >= 2:
                value = self.floatValue(data[0:2])
                if self.verbose:
                    logging.debug("temp: {}" .format(value))
                self.temperature = value / 100.0
                    
            if len(data) >= 3:
                value = int(data[2])
                if self.verbose:
                    logging.debug("hum: {}" .format(value))
                self.humidity = value
                    
            if len(data) >= 4:
                value = int(data[3])
                if self.verbose:
                    logging.debug("bat: {}" .format(value))
                self.battery = value
            return True
        except:
            logging.warning(sys.exc_info(), exc_info=True)
        return False
