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
# GUI
import tkinter as tk
import tkinter.font as tkFont

observer = None

import ble_temperature_sensor
# from .sensor import Sensor
# from .sensortype import SensorType


class BluetoothTemperatureSensor(tk.Frame):
    fontsize = 20
    font = None
    updatetime = 60
    sensors = []
    sensorLabels = {}
    temperature = None
    humidity = None
    battery = None
    fg = "black"
    bg = "white"
    verbose = False
    gui = "graphics"  # graphics or text

    def __init__(self, master=None, fontsize=20, updatetime=60,
                 gui="graphics", font=None, bg=None, fg=None, verbose=False):
        self.fontsize = fontsize
        self.font = font
        self.updatetime = updatetime
        self.verbose = verbose
        self.gui = gui
        if fg is not None:
            self.fg = fg
        if bg is not None:
            self.bg = bg
        if master is not None:
            # No GUI
            tk.Frame.__init__(self, master)
            self.initUI()
            self.pack()

        threading.Thread(target=self.update).start()

    def initUI(self):
        if self.gui == "graphics":
            if self.font is None:
                logging.debug("create font")
                self.font = tkFont.Font(family="Lucida Grande", size=self.fontsize)

            self.pack(side=tk.TOP, fill=tk.X)

    def updateGUI(self):
        try:
            for sensor in self.sensors:
                self.updateGUISensor(sensor)
        except:
            logging.error(sys.exc_info(), exc_info=True)
            
    def updateGUISensor(self, sensor):
        try:
            if self.gui == "graphics":
                if sensor not in self.sensorLabels:
                    if self.verbose:
                        logging.info("label created: {}".format(sensor.name))
                    frame = tk.Frame(master=self, bg=self.bg)  # , bg='red')
                    frame.pack(side=tk.TOP, fill=tk.X)
                    label = tk.Label(frame, text=sensor.name + ":", font=self.font, bg=self.bg, fg=self.fg)
                    label.pack(side=tk.LEFT)
                    self.sensorLabels[sensor] = tk.Label(frame, text="--° --%", font=self.font, anchor=tk.W, fg=self.fg, bg=self.bg)
                    self.sensorLabels[sensor].pack(side=tk.RIGHT, fill=tk.X)
                    self.pack();
                if sensor.temperature is not None and sensor.humidity is not None:
                    # logging.info("change: {} {:.1f}° {:.0f}%".format(sensor.name, sensor.temperature, sensor.humidity))
                    self.sensorLabels[sensor]['text'] = "{:.1f}° {:.0f}%".format(sensor.temperature, sensor.humidity)
            else:
                text = ""
                if sensor.name is not None:
                    text += sensor.name + ": "
                else:
                    text += "--: "
                if sensor.temperature is not None:
                    text += "{:.1f}° ".format(sensor.temperature)
                else:
                    text += "--.-° "
                if sensor.humidity is not None:
                    "{:.0f}%".format(sensor.humidity)
                else:
                    text += "--%"
                print(text)
        except:
            logging.error(sys.exc_info(), exc_info=True)
            
    def addSensor(self, sensor):
        self.sensors.append(sensor)
        self.updateGUISensor(sensor)
        
    def getSensorByName(self, name):
        for sensor in self.sensors:
            if sensor.name == name:
                return sensor
        return None

    def floatValue100(self, nums):
        # check if value is negative
        num = (nums[1] << 8) | nums[0]
        if nums[1] == 0xff:
            num = -((num ^ 0xffff) + 1)
        return float(num / 100.0)
    
    def floatValue(self, nums):
        # check if value is negative
        num = (nums[1] << 8) | nums[0]
        if nums[1] == 0xff:
            num = -((num ^ 0xffff) + 1)
        return num
    
    def twosComplement(self, n: int, w: int=16) -> float:
        """Two's complement integer conversion."""
        # Adapted from: https://stackoverflow.com/a/33716541.
        if n & (1 << (w - 1)):
            n = n - (1 << w)
        return n / 100.0
    
    def floatValue1000(self, nums):
        # check if value is negative
        num = (nums[1] << 8) | nums[0]
        if nums[1] == 0xff:
            num = -((num ^ 0xffff) + 1)
        return float(num) / 1000

    def floatValue2(self, nums):
        num = int(nums[2:4] + nums[0:2], 16)
        num_bits = 16
        if num & (1 << (num_bits - 1)):
            num -= 1 << num_bits
        return float(num) / 100

    def update(self):
        global observer
        
        if observer is None:
            # wait for main-thread
            time.sleep(5)
            try:
                adapter = get_provider().get_adapter()

                observer = Observer(adapter)
                observer.on_advertising_data = self.onData
                if self.verbose:
                    logging.info("observer started")
                while True:
                    try:
                        observer.start()
                        time.sleep(5)
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
                found = False
                for sensor in self.sensors:
                    if advertisement.address.address.lower() == sensor.address:
                        if sensor.type is ble_temperature_sensor.SensorType.GOVEE:
                            if len(advertisement.mfg_data) >= 11:
                                temp, hum, batt = struct.unpack_from("<HHB", advertisement.mfg_data, 6)
                                if self.verbose:
                                    logging.info("govee {} {} {} {} {}".format(sensor.name,
                                                                               self.floatValue100(advertisement.mfg_data[0:2]),
                                                                               self.twosComplement(temp),
                                                                               hum / 100.0,
                                                                               batt))
                                sensor.temperature = float(self.twosComplement(temp))
                                # sensor.temperature = self.floatValue100(advertisement.mfg_data[0:2]) / 100.0
                                sensor.humidity = float(hum / 100.0)
                                sensor.battery = batt
                                self.updateGUISensor(sensor)
                                found = True
                        elif sensor.type is ble_temperature_sensor.SensorType.INKBIRD:
                            # blescan -> sps
                            if len(advertisement.mfg_data) >= 7:
                                # temp = self.floatValue100(advertisement.mfg_data[0:2])
                                temp = float(int.from_bytes(advertisement.mfg_data[0:2], byteorder='little', signed=True) / 100.0)
                                hum = self.floatValue100(advertisement.mfg_data[2:4])
                                if  self.verbose:
                                    logging.info("inkbird {} {:.1f}° {:.0f}% {}".format(sensor.name, temp, hum, advertisement.mfg_data))
                                sensor.temperature = float(temp)
                                sensor.humidity = float(hum)
                                # TODO battery
                                self.updateGUISensor(sensor)
                                found = True
                        elif sensor.type is ble_temperature_sensor.SensorType.BRIFIT:
                            # blescan -> ThermoBeacon
                            # logging.info("brifit data: {} {} {}".format(advertisement.address.address, len(advertisement.mfg_data), advertisement.mfg_data))
                            if len(advertisement.mfg_data) == 20:
                                batt, temp, hum = struct.unpack('<HhH', advertisement.mfg_data[10:16])
                                if self.verbose:
                                    logging.info("brifit1 {} {:.1f}° {:.0f}%".format(sensor.name, temp / 16.0, hum / 16.0))
                                sensor.temperature = float(temp / 16.0)
                                sensor.humidity = float(hum / 16.0)
                                
                                if False:
                                    temp = self.floatValue100(advertisement.mfg_data[0:2])
                                    hum = self.floatValue100(advertisement.mfg_data[2:4])
                                    logging.info("brifit2 {} {:.1f}° {:.0f}%".format(sensor.name, temp, hum))
                                    # sensor.temperature = float(temp)
                                    # sensor.humidity = float(hum)
                                # TODO battery
                                self.updateGUISensor(sensor)
                                found = True
                        elif sensor.type is ble_temperature_sensor.SensorType.AZARTON:
                            # blescan -> ThermoBeacon
                            # logging.info("brifit data: {} {} {}".format(advertisement.address.address, len(advertisement.mfg_data), advertisement.mfg_data))
                            if len(advertisement.mfg_data) == 20:
                                batt, temp, hum = struct.unpack('<HhH', advertisement.mfg_data[10:16])
                                if self.verbose:
                                    logging.info("azarton {} {:.1f}° {:.0f}%".format(sensor.name, temp / 16.0, hum / 16.0))
                                sensor.temperature = float(temp / 16.0)
                                sensor.humidity = float(hum / 16.0)
                                
                                # TODO battery
                                self.updateGUISensor(sensor)
                                found = True
                        else:
                            logging.error("unknown sensortype {}".format(sensor.type))
                if not found:
                    if self.verbose:
                        logging.debug("wrong mac: {} {} {}".format(advertisement.address.address, len(advertisement.mfg_data), advertisement.mfg_data.hex()))
                           
        except:
            logging.error(sys.exc_info(), exc_info=True)


def main():
    if True:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s')

        if False:
            root = tk.Tk()
            sensors = BluetoothTemperatureSensor(master=root, gui="graphics")
            sensors.addSensor(ble_temperature_sensor.Sensor(name="Gefrier", address="49:42:07:00:21:a8", type=ble_temperature_sensor.SensorType.INKBIRD))
            root.mainloop()

        if True:
            sensors = BluetoothTemperatureSensor(gui="text", verbose=True)
            sensors.addSensor(ble_temperature_sensor.Sensor(name="Gefrier", address="49:42:07:00:21:a8", type=ble_temperature_sensor.SensorType.INKBIRD))
            sleep(1000000);
        
        if False:
            sensors = BluetoothTemperatureSensor(gui="text", verbose=True)
            sensors.addSensor(ble_temperature_sensor.Sensor(name="Innen", address="A4:C1:38:DF:CB:2C", type=ble_temperature_sensor.SensorType.AZARTON))
            sleep(1000000);
        

if __name__ == '__main__':
    main()

