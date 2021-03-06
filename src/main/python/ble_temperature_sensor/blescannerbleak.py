#!/usr/bin/env python3

import sys
sys.path.append('..')

import ble_temperature_sensor
from time import sleep
import logging
import threading
import time
# bluetooth
import bleak
import asyncio
import re


class BluetoothScannerBleak():
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

    async def updateBleak(self):
        while True:
            try:
                logging.info("create scanner")
                if True:
                    async with bleak.BleakScanner() as scanner:
                        scanner._bus.add_message_handler(self.parseMessage)
                        await asyncio.sleep(120.0)
                else:
                     scanner = bleak.BleakScanner()
                     scanner.register_detection_callback(self.detectionCallback)
                     await scanner.start()
                     await asyncio.sleep(120.0)
                     await scanner.stop()
            except:
                logging.error(sys.exc_info(), exc_info=True)
                
    def detectionCallback(self, device, advertisement_data):
        logging.info("address: {} RSSI: {} addata: {} svdata: {}".format(device.address, device.rssi, advertisement_data, advertisement_data.service_data))
    
    def parseMessage(self, message):
            # logging.info("message: {}".format(message))
            # logging.info("message-member: {}".format(message.member))
            # logging.info("message-path: {}".format(message.path))
            if message.path:
                mac = re.sub(r"^.*/dev_", "", message.path).replace("_", ":").upper()
                # if mac == "E9:54:00:00:02:BE":
                if True:
                    # logging.info("message-mac: {}".format(mac))
                    logging.info("message body: {} {} {}".format(mac, message.member, message.body))
                    if "PropertiesChanged" == message.member:
                        body = message.body;
                        if body:
                            # logging.info("body: {}".format(type(body)))
                            if type(body) == list:
                                for i in body:
                                    # logging.info("body i: {}".format(type(i)))
                                    if type(i) == dict:
                                        # logging.info("body i: {}".format(i.keys()))
                                        # logging.info("body i: {}".format(i))
                                        # logging.info("body md: {}".format(i.get("ManufacturerData")))
                                        md = i.get("ManufacturerData")
                                        # md = i["ManufacturerData"]
                                        if md:
                                            # logging.info("md: {}".format(md))
                                            # logging.info("md: {}".format(type(md)))
                                            if md.value:
                                                # logging.info("value: {}".format(type(md.value)))
                                                if type(md.value) == dict: 
                                                    v = md.value.popitem()
                                                    logging.info("value: {}".format(v))
                                                    # logging.info("value: {}".format(type(v)))
                                                    if len(v) == 2:
                                                        key = v[0]
                                                        # logging.info("key: {} {}".format(mac, v[0]))
                                                        v = v[1].value
                                                        # logging.info("value: {}".format(v))
                                                        # logging.info("value: {}".format(type(v)))
                                                        if type(v) == bytes:
                                                            # logging.info("value: {} {} {}".format(len(v), type(v), v.hex()))
                                                            prefix = key.to_bytes(2, byteorder='little')
                                                            logging.info("prefix: {} {} {}".format(mac, key, prefix))
                                                            self.onData(mac, prefix + v)
                                                            return
                    logging.info("unknown message body: {} {} {}".format(mac, message.member, message.body))
                    
    def update(self):
        asyncio.run(self.updateBleak())

    def onData(self, mac, data):
        try:
            if data is not None:
                if self.verbose:
                    logging.info("data from {}: {} {}".format(mac.lower(), len(data), data.hex()))
                found = False
                for sensor in self.sensors:
                    if mac.lower() == sensor.address.lower():
                        parsed = sensor.parseData(data)
                        if parsed and sensor.callbackAfterData is not None:
                            sensor.callbackAfterData()
                        found = True
                if not found:
                    if self.verbose:
                        logging.info("wrong mac: {} {} {}".format(mac, len(data), data.hex()))
                           
        except:
            logging.error(sys.exc_info(), exc_info=True)


def main():
    if True:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s')
        # logging.getLogger().setLevel(logging.INFO)

        logging.info("start")
        scanner = BluetoothScannerBleak(verbose=True)
        sensor = ble_temperature_sensor.SensorInkbird(name="Grau", address="10:08:2C:21:DF:0C", verbose=True)
        scanner.addSensor(sensor)
        sensor = ble_temperature_sensor.SensorBrifit(name="Ventil", address="E9:54:00:00:02:BE", verbose=True)
        scanner.addSensor(sensor)
        
        while True:
            time.sleep(10)
        

if __name__ == '__main__':
    main()

