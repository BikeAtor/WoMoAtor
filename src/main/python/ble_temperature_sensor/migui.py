#!/usr/bin/env python3

import sys
sys.path.append('..')
sys.path.append('C:/msys64/mingw64/bin')
import os
os.environ['PATH'] = 'C:/msys64/mingw64/bin' + os.pathsep + os.environ['PATH']

import os
import logging
import threading
import time
import ble_temperature_sensor
import atorlib

# GUI
import tkinter as tk
import tkinter.font as tkFont
# import cairosvg
import io
from PIL import Image, ImageTk

useGi = False
try:
    from gi.repository import GObject
    from gi.repository import GLib
except:
    logging.info("no gi")
    useGi = False
    pass


class MiGUI(atorlib.GuiIconValueBattery):
    misensor = None
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
                verbose=False,
                useBleak: bool=True):
        if valueNewline is not None:
            self.valueNewline = valueNewline
        try:
            logging.debug("before sensor")
            if useBleak:
                self.misensor = ble_temperature_sensor.MiSensorBleak(mac=mac, name=name,
                                                                 verbose=verbose,
                                                                 updatetimeS=updatetimeS,
                                                                 callbackAfterData=self.updateGUI,
                                                                 disconnectAfterData=disconnectAfterData)
            else:
                self.misensor = ble_temperature_sensor.MiSensorBluepy(mac=mac, name=name,
                                                                 verbose=verbose,
                                                                 updatetimeS=updatetimeS,
                                                                 callbackAfterData=self.updateGUI,
                                                                 disconnectAfterData=disconnectAfterData)
            self.misensor.startReading()
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
        if self.verbose:
            logging.info("start")
        text = "--° --%"
        if self.valueNewline:
            # logging.info("newline")
            text = "--°\n--%"
        if self.misensor is not None:
            sensor = self.misensor.getSensor()
            if sensor.temperature is not None and sensor.humidity is not None:
                # logging.info("change: {} {:.1f}° {:.0f}%".format(sensor.name, sensor.temperature, sensor.humidity))
                if self.valueNewline:
                    text = "{:.1f}°\n{:.0f}%".format(sensor.temperature, sensor.humidity)
                else:
                    text = "{:.1f}° {:.0f}%".format(sensor.temperature, sensor.humidity)
            else:
                logging.info("no values")
        return text
    
    def no_getIconText(self):
        # add battery
        text = super().getIconText()
        if self.misensor is not None:
            sensor = self.misensor.getSensor()
            if sensor.battery is not None:
                if text is None:
                    text = ""
                text += "\n{}%".format(sensor.battery)
        return text
    
    def getBatteryLevel(self):
        if self.verbose:
            logging.info("start")
        if self.misensor is not None:
            sensor = self.misensor.getSensor()
            if sensor.battery is not None:
                return sensor.battery
        return None
        
    def getSensor(self):
        return self.misensor
        
    def toJSON(self, prefix="battery"):
        if self.misensor is not None:
            return self.misensor.toJSON(prefix)
        return ""
        

def onClosingMisensor():
    root.destroy()
    os._exit(os.EX_OK)

        
def main():
    try:
        global root
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s')
        logging.getLogger().setLevel(logging.DEBUG)
        
        root = tk.Tk()
        fontMedium = tkFont.Font(family="TkFixedFont", size=14, weight="bold")
        root.protocol("WM_DELETE_WINDOW", onClosingMisensor)
        frame = tk.Frame(root)
        frame.pack(side=tk.TOP, fill=tk.X)
        
        useBleak = False
        # kühlschrank
        mac = "58:2d:34:39:1a:c2"
        # Speicher
        mac = "58:2d:34:39:17:d2"
        app = MiGUI(master=frame, mac=mac,
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
                        updatetimeS=10,
                        verbose=True,
                        useBleak=useBleak)
        if useBleak and useGi:
            # create the dbus loop (must be global so we can terminate it)
            # GObject.timeout_add(100, dbus_timeout_periodic)
            if sys.version_info >= (3, 9):
                dbus_loop = GLib.MainLoop()
            else:
                dbus_loop = GObject.MainLoop()

            # ##Finally: start the dbus thread and then the Tk main loop
            dbus_thread = threading.Thread(target=dbus_loop.run)
            dbus_thread.start()
            logging.info("tk+glib mainloop")
            root.mainloop()
        else:
            logging.info("mainloop")
            root.mainloop()
            logging.info("after mainloop")
        while(True):
            time.sleep(10000)
    except:
        logging.info(sys.exc_info(), exc_info=True)


if __name__ == '__main__':
    main()
