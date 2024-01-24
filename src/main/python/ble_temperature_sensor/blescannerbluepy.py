#!/usr/bin/env python3

import sys
from time import sleep
sys.path.append('..')

import ble_temperature_sensor

import logging
import threading
import time
# bluetooth
from bleson import get_provider, Observer
import struct

observer = None


class BluetoothScannerBluepy():
    updatetime = 60
    sensors = []
    sensorLabels = {}
    verbose = False
    adapter: int = 0
 
    def __init__(self, adapter: int=0, updatetime=60, verbose=False):
        self.adapter = adapter
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
                adapter = get_provider().get_adapter(adapter_id=self.adapter)

                observer = Observer(adapter, self.onData)
                # observer.on_advertising_data = self.onData
                logging.info("observer created. adapter: {}".format(self.adapter))
                
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
            if advertisement.service_data:
                if self.verbose:
                    logging.info("service_data from {}: {}".format(advertisement.address.address.lower(), advertisement.service_data.hex()))
                found = False
                for sensor in self.sensors:
                    if advertisement.address.address.lower() == sensor.address.lower():
                        parsed = sensor.parseServiceData(advertisement.service_data)
                        if parsed and sensor.callbackAfterData is not None:
                            sensor.callbackAfterData()
                        found = True
                if not found:
                    if self.verbose:
                        if advertisement.mfg_data:
                            logging.info("wrong mac: {} {} {}".format(advertisement.address.address, len(advertisement.mfg_data), advertisement.mfg_data.hex()))
                        else:
                            logging.info("wrong mac: {}".format(advertisement.address.address))

            if advertisement.mfg_data:
                if self.verbose:
                    logging.info("mfg_data from {}: {}".format(advertisement.address.address.lower(), advertisement.mfg_data.hex()))
                found = False
                for sensor in self.sensors:
                    if advertisement.address.address.lower() == sensor.address.lower():
                        parsed = sensor.parseData(advertisement.mfg_data)
                        if parsed and sensor.callbackAfterData is not None:
                            sensor.callbackAfterData()
                        found = True
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
        scanner = BluetoothScannerBluepy(verbose=False)
        sensor = ble_temperature_sensor.SensorInkbird(name="Grau", address="10:08:2C:21:DF:0C", verbose=True)
        scanner.addSensor(sensor)
        sensor = ble_temperature_sensor.SensorBrifit(name="Ventil", address="E9:54:00:00:02:BE", verbose=True)
        scanner.addSensor(sensor)
        
        while True:
            time.sleep(10)
        

if __name__ == '__main__':
    main()

