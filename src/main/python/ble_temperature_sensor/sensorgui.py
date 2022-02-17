#!/usr/bin/env python3

import sys
sys.path.append('..')

import os
import logging
import threading
import time
import ble_temperature_sensor
import atorlib

# GUI
import tkinter as tk
import tkinter.font as tkFont
import tkinter.tix as tix
import cairosvg
import io
from PIL import Image, ImageTk


class SensorGUI(atorlib.GuiIconValueBattery):
    sensor = None
    valueNewline = False

    def __init__(self, balloon=None,
                sensor=None,
                batteryIconName1=None,
                batteryIconName2=None,
                batteryIconName3=None,
                batteryIconName4=None,
                master=None, size=(500, 500),
                name=None, showName=True,
                gui="graphic", orientation="vertical",
                valueNewline=None,
                iconName="pic_free/thermometer_pixabay_clone.png",
                disconnectAfterData=False,
                timeout=5, updatetimeS=60,
                font=None, fontsize=20,
                fontIconLabel=None,
                bg=None, fg=None,
                verbose=False):
        if valueNewline is not None:
            self.valueNewline = valueNewline
        self.sensor = sensor
        self.sensor.callbackAfterData = self.updateGUI
        super().__init__(balloon=balloon,
                        batteryIconName1=batteryIconName1,
                        batteryIconName2=batteryIconName2,
                        batteryIconName3=batteryIconName3,
                        batteryIconName4=batteryIconName4,
                        master=master, size=size, name=name, showName=showName,
                        gui=gui, orientation=orientation, iconName=iconName, disconnectAfterData=disconnectAfterData,
                        timeout=timeout, fontsize=fontsize, updatetimeS=updatetimeS,
                        font=font, fontIconLabel=fontIconLabel,
                        bg=bg, fg=fg,
                        verbose=verbose)
    
    def getText(self):
        text = "--° --%"
        if self.valueNewline:
            # logging.info("newline")
            text = "--°\n--%"
        if self.sensor is not None:
            sensor = self.sensor
            if sensor.temperature is not None and sensor.humidity is not None:
                # logging.info("change: {} {:.1f}° {:.0f}%".format(sensor.name, sensor.temperature, sensor.humidity))
                if self.valueNewline:
                    text = "{:.1f}°\n{:.0f}%".format(sensor.temperature, sensor.humidity)
                else:
                    text = "{:.1f}° {:.0f}%".format(sensor.temperature, sensor.humidity)
        return text
    
    def no_getIconText(self):
        # add battery
        text = super().getIconText()
        if self.sensor is not None:
            sensor = self.sensor
            if sensor.battery is not None:
                if text is None:
                    text = ""
                text += "\n{}%".format(sensor.battery)
        return text
    
    def getBatteryLevel(self):
        if self.sensor is not None:
            sensor = self.sensor
            if sensor.battery is not None:
                return sensor.battery
        return None
        
    def getSensor(self):
        return self.sensor
        
    def toJSON(self, prefix="battery"):
        if self.sensor is not None:
            return self.sensor.toJSON(prefix)
        return ""
        

def onClosingSensor():
    root.destroy()
    os._exit(os.EX_OK)

        
def main():
    try:
        global root
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s')
        logging.getLogger().setLevel(logging.DEBUG)
        
        root = tix.Tk()
        fontMedium = tkFont.Font(family="TkFixedFont", size=14, weight="bold")
        root.protocol("WM_DELETE_WINDOW", onClosingSensor)
        frame = tk.Frame(root)
        frame.pack(side=tk.TOP, fill=tk.X)
        balloon = tix.Balloon(root)
    
        if True:
            sensor = ble_temperature_sensor.Sensor()
            sensor.name = "Tescht"
            sensor.temperature = 34.56
            sensor.humidity = 70.0
            sensor.battery = 10.1
            SensorGUI(sensor=sensor,
                        master=frame,
                        balloon=balloon,
                        name=sensor.name,
                        gui="graphic",
                        # orientation="vertical",
                        orientation="horizontal",
                        size=(150, 60),
                        fontsize=10,
                        # gui="graphic", orientation="horizontal", size=(400, 100),
                        # gui="text", orientation="text", size=(400, 100),
                        iconName="../pic_free/sensor_pixabay_clone.png",
                        batteryIconName1="../pic_free/battery_1_pixabay_clone.png",
                        batteryIconName2="../pic_free/battery_2_pixabay_clone.png",
                        batteryIconName3="../pic_free/battery_3_pixabay_clone.png",
                        batteryIconName4="../pic_free/battery_4_pixabay_clone.png",
                        # disconnectAfterData=False,
                        disconnectAfterData=True,
                        updatetimeS=20,
                        verbose=True)
            SensorGUI(sensor=sensor,
                        master=frame,
                        # name=sensor.name,
                        gui="graphic",
                        # orientation="vertical",
                        orientation="horizontal",
                        size=(150, 40),
                        fontsize=10,
                        # gui="graphic", orientation="horizontal", size=(400, 100),
                        # gui="text", orientation="text", size=(400, 100),
                        iconName="../pic_free/thermometer_pixabay_clone.png",
                        batteryIconName1="../pic_free/battery_1_pixabay_clone.png",
                        batteryIconName2="../pic_free/battery_2_pixabay_clone.png",
                        batteryIconName3="../pic_free/battery_3_pixabay_clone.png",
                        batteryIconName4="../pic_free/battery_4_pixabay_clone.png",
                        # disconnectAfterData=False,
                        disconnectAfterData=True,
                        updatetimeS=20,
                        verbose=True)
            
        if False:
            scanner = ble_temperature_sensor.BluetoothScanner(verbose=False)
            sensor = None
            sensor = ble_temperature_sensor.SensorInkbird(name="Grau", address="10:08:2C:21:DF:0C", verbose=True)
            scanner.addSensor(sensor)
            sensor2 = None
            sensor2 = ble_temperature_sensor.SensorBrifit(name="Ventil", address="E9:54:00:00:02:BE", verbose=True)
            scanner.addSensor(sensor2)
            
            if sensor is not None:
                SensorGUI(sensor=sensor,
                        master=frame,
                        name=sensor.name,
                        gui="graphic",
                        # orientation="vertical",
                        orientation="horizontal",
                        size=(240, 320),
                        # gui="graphic", orientation="horizontal", size=(400, 100),
                        # gui="text", orientation="text", size=(400, 100),
                        iconName="../pic_free/thermometer_pixabay_clone.png",
                        batteryIconName1="../pic_free/battery_1_pixabay_clone.png",
                        batteryIconName2="../pic_free/battery_2_pixabay_clone.png",
                        batteryIconName3="../pic_free/battery_3_pixabay_clone.png",
                        batteryIconName4="../pic_free/battery_4_pixabay_clone.png",
                        # disconnectAfterData=False,
                        disconnectAfterData=True,
                        updatetimeS=20,
                        verbose=True)
            if sensor2 is not None:
                SensorGUI(sensor=sensor2,
                        master=frame,
                        name=sensor2.name,
                        gui="graphic",
                        # orientation="vertical",
                        orientation="horizontal",
                        size=(240, 320),
                        # gui="graphic", orientation="horizontal", size=(400, 100),
                        # gui="text", orientation="text", size=(400, 100),
                        iconName="../pic_free/thermometer_pixabay_clone.png",
                        batteryIconName1="../pic_free/battery_1_pixabay_clone.png",
                        batteryIconName2="../pic_free/battery_2_pixabay_clone.png",
                        batteryIconName3="../pic_free/battery_3_pixabay_clone.png",
                        batteryIconName4="../pic_free/battery_4_pixabay_clone.png",
                        # disconnectAfterData=False,
                        disconnectAfterData=True,
                        updatetimeS=20,
                        verbose=True)
            
        if False:
            sensors = ble_temperature_sensor.BluetoothTemperatureSensor(frame)
            sensor = ble_temperature_sensor.Sensor(name="Gefrier", address="e9:47:00:00:22:c2", type=ble_temperature_sensor.SensorType.BRIFIT)
            sensors.addSensor(sensor)
        
            app = SensorGUI(sensor=sensor,
                        master=frame,
                        name=sensor.name,
                        gui="graphic",
                        # orientation="vertical",
                        orientation="horizontal",
                        size=(240, 320),
                        # gui="graphic", orientation="horizontal", size=(400, 100),
                        # gui="text", orientation="text", size=(400, 100),
                        iconName="../pic_free/thermometer_pixabay_clone.png",
                        batteryIconName1="../pic_free/battery_1_pixabay_clone.png",
                        batteryIconName2="../pic_free/battery_2_pixabay_clone.png",
                        batteryIconName3="../pic_free/battery_3_pixabay_clone.png",
                        batteryIconName4="../pic_free/battery_4_pixabay_clone.png",
                        # disconnectAfterData=False,
                        disconnectAfterData=True,
                        updatetimeS=20,
                        verbose=True)
            
        logging.info("mainloop")
        root.mainloop()
        logging.info("after mainloop")
        while(True):
            time.sleep(10000)
    except:
        logging.info(sys.exc_info(), exc_info=True)


if __name__ == '__main__':
    main()
