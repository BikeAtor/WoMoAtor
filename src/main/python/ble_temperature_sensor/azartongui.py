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
import cairosvg
import io
from PIL import Image, ImageTk


class AzartonGUI(atorlib.GuiIconValueBattery):
    azartonsensor = None
    valueNewline = False

    def __init__(self, balloon=None,
                batteryIconName1=None,
                batteryIconName2=None,
                batteryIconName3=None,
                batteryIconName4=None,
                master=None, mac=None, size=(500, 500),
                name=None, showName=True,
                gui="graphic", orientation="vertical",
                valueNewline=None,
                iconName="pic_free/thermometer_pixabay_clone.png",
                disconnectAfterData=False,
                timeout=5, fontsize=20, updatetimeS=60,
                font=None, bg=None, fg=None,
                verbose=False):
        if valueNewline is not None:
            self.valueNewline = valueNewline
        try:
            logging.debug("before sensor")
            self.azartonsensor = ble_temperature_sensor.AzartonSensor(mac=mac, name=name,
                                                                 verbose=verbose,
                                                                 updatetimeS=updatetimeS,
                                                                 callbackAfterData=self.updateGUI,
                                                                 disconnectAfterData=disconnectAfterData)
            self.azartonsensor.startReading()
            logging.info("after sensor")
        except:
            logging.error(sys.exc_info(), exc_info=True)
        super().__init__(balloon=balloon,
                        batteryIconName1=batteryIconName1,
                        batteryIconName2=batteryIconName2,
                        batteryIconName3=batteryIconName3,
                        batteryIconName4=batteryIconName4,
                        master=master, size=size, name=name, showName=showName,
                        gui=gui, orientation=orientation,
                        iconName=iconName, disconnectAfterData=disconnectAfterData,
                        timeout=timeout, fontsize=fontsize, updatetimeS=updatetimeS,
                        font=font, bg=bg, fg=fg,
                        verbose=verbose)
    
    def getText(self):
        text = "--° --%"
        if self.valueNewline:
            # logging.info("newline")
            text = "--°\n--%"
        if self.azartonsensor is not None:
            sensor = self.azartonsensor.getSensor()
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
        if self.azartonsensor is not None:
            sensor = self.azartonsensor.getSensor()
            if sensor.battery is not None:
                if text is None:
                    text = ""
                text += "\n{}%".format(sensor.battery)
        return text
    
    def getBatteryLevel(self):
        logging.info("start")
        if self.azartonsensor is not None:
            sensor = self.azartonsensor.getSensor()
            if sensor.battery is not None:
                return sensor.battery
        return None
        
    def getSensor(self):
        return self.azartonsensor
        
    def toJSON(self, prefix="battery"):
        if self.azartonsensor is not None:
            return self.azartonsensor.toJSON(prefix)
        return ""
        

def onClosingAzartonsensor():
    root.destroy()
    os._exit(os.EX_OK)

        
def main():
    try:
        global root
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s')
        logging.getLogger().setLevel(logging.DEBUG)
        
        root = tk.Tk()
        fontMedium = tkFont.Font(family="TkFixedFont", size=14, weight="bold")
        root.protocol("WM_DELETE_WINDOW", onClosingAzartonsensor)
        frame = tk.Frame(root)
        frame.pack(side=tk.TOP, fill=tk.X)
    
        mac = "A4:C1:38:DF:CB:2C"
        app = AzartonGUI(master=frame, mac=mac,
                        name="Innen",
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
