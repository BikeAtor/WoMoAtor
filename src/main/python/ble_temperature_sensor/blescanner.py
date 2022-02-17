#!/usr/bin/env python3

import sys
from time import sleep
sys.path.append('.')
sys.path.append('..')
sys.path.append('ble_temperature_sensor')
sys.path.append('lib')

import logging
import threading
import time
# bluetooth
from bleson import get_provider, Observer
import struct

observer = None

import ble_temperature_sensor


class BluetoothScanner():
    updatetime = 60
    sensors = []
    sensorLabels = {}
    verbose = False
 
    def __init__(self, updatetime=60, verbose=False):
        self.updatetime = updatetime
        self.verbose = verbose
        threading.Thread(target=self.update).start()
            
    def addSensor(self, sensor):
        self.sensors.append(sensor)
        
    def getSensorByName(self, name):
        for sensor in self.sensors:
            if sensor.name == name:
                return sensor
        return None

    def update(self):
        global observer
        
        if observer is None:
            # wait for main-thread
            time.sleep(5)
            try:
                adapter = get_provider().get_adapter()

                observer = Observer(adapter)
                observer.on_advertising_data = self.onData
                logging.info("observer created")
                
                while True:
                    try:
                        if self.verbose:
                            logging.info("observer start")
                        observer.start()
                        time.sleep(5)
                        if self.verbose:
                            logging.info("observer stop")
                        observer.stop()
                    except:
                        logging.error(sys.exc_info(), exc_info=True)
                    time.sleep(self.updatetime)
            except:
                logging.error(sys.exc_info(), exc_info=True)
        else:
            if self.verbose:
                logging.info("observer already started")

    def onData(self, advertisement):
        try:
            if advertisement.mfg_data is not None:
                if self.verbose:
                    logging.info("data from {}: {}".format(advertisement.address.address.lower(), advertisement.mfg_data))
                found = False
                for sensor in self.sensors:
                    if advertisement.address.address.lower() == sensor.address.lower():
                        parsed = sensor.parseData(advertisement.mfg_data)
                        if parsed and sensor.callbackAfterData is not None:
                            sensor.callbackAfterData()
                if not found:
                    if self.verbose:
                        logging.info("wrong mac: {} {} {}".format(advertisement.address.address, len(advertisement.mfg_data), advertisement.mfg_data.hex()))
                           
        except:
            logging.error(sys.exc_info(), exc_info=True)


def main():
    if True:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s')
        # logging.getLogger().setLevel(logging.INFO)

        logging.info("start")
        scanner = BluetoothScanner(verbose=False)
        sensor = ble_temperature_sensor.SensorInkbird(name="Grau", address="10:08:2C:21:DF:0C", verbose=True)
        scanner.addSensor(sensor)
        sensor = ble_temperature_sensor.SensorBrifit(name="Ventil", address="E9:54:00:00:02:BE", verbose=True)
        scanner.addSensor(sensor)
        
        while True:
            time.sleep(10)
        

if __name__ == '__main__':
    main()

