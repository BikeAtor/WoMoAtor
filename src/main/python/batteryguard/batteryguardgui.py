#!/usr/bin/env python3

import sys
sys.path.append('..')

import os
import logging
import threading
import time
import batteryguard
import atorlib

# GUI
import tkinter as tk
import tkinter.font as tkFont
import cairosvg
import io
from PIL import Image, ImageTk


class BatteryGuardGUI(atorlib.GuiIconValue):
    batteryguard = None

    def __init__(self, master=None, mac=None, size=(500, 500),
                name=None,
                gui="graphic", orientation="vertical",
                iconName="pic_free/battery2_pixabay_clone.png",
                disconnectAfterData=False,
                timeout=5, fontsize=20, updatetimeS=60,
                font=None, bg=None, fg=None,
                verbose=False):
        super().__init__(master=master, size=size, name=name,
                         gui=gui, iconName=iconName, disconnectAfterData=disconnectAfterData,
                         timeout=timeout, fontsize=fontsize, updatetimeS=updatetimeS,
                         font=font, bg=bg, fg=fg,
                         verbose=verbose)
        try:
            logging.debug("before batteryguard")
            self.batteryguard = batteryguard.BatteryGuard(mac=mac, name=name,
                                                                 verbose=self.verbose,
                                                                 updatetimeS=self.updatetimeS,
                                                                 callbackAfterData=self.updateGUI,
                                                                 disconnectAfterData=self.disconnectAfterData)
            self.batteryguard.startReading()
            logging.debug("after batteryguard")
        except:
            logging.error(sys.exc_info(), exc_info=True)
    
    def getText(self):
        text = "--V"
        if self.batteryguard is not None:
            text = ""
            voltage = self.batteryguard.getVoltage()
            if voltage is None:
                text += "--V"
            else:
                text += "{:.2f}V".format(voltage)
        return text
        
    def getBatteryguard(self):
        return self.batteryguard
        
    def toJSON(self, prefix="battery"):
        if self.batteryguard is not None:
            return self.batteryguard.toJSON(prefix)
        return ""
        

def onClosingBatteryguard():
    root.destroy()
    os._exit(os.EX_OK)

        
def main():
    try:
        global root
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s')

        root = tk.Tk()
        fontMedium = tkFont.Font(family="TkFixedFont", size=14, weight="bold")
        root.protocol("WM_DELETE_WINDOW", onClosingBatteryguard)
        frame = tk.Frame(root)
        frame.pack(side=tk.TOP, fill=tk.X)
    
        mac = "c8:fd:19:41:29:6b"
        app = BatteryGuardGUI(master=frame, mac=mac,
                        name="Auto",
                        gui="graphic", orientation="vertical", size=(240, 320),
                        # gui="graphic", orientation="horizontal", size=(400, 100),
                        # gui="text", orientation="text", size=(400, 100),
                        iconName="../pic_free/battery2_pixabay_clone.png",
                        disconnectAfterData=True,
                        updatetimeS=5,
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
