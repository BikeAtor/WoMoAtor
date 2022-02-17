#!/usr/bin/env python3

""" NOT WORKING """

import time
from bluepy import btle
import logging
import threading
# GUI
import tkinter as tk
import tkinter.font as tkFont


class InkbirdTH2(tk.Frame):
    fontsize = 20
    font = None
    startuptime = 3
    updatetime = 60
    mac = None
    temperature = None
    humidity = None
    battery = None
    fg = "black"
    bg = "white"

    def __init__(self, master=None, mac=None, fontsize=20, updatetime=60, font=None, bg=None, fg=None):
        self.mac = mac
        self.fontsize = fontsize
        self.updatetime = updatetime
        self.font = font
        if fg is not None:
            self.fg = fg
        if bg is not None:
            self.bg = bg
        if master is not None:
            # No GUI
            tk.Frame.__init__(self, master, bg=self.bg)
            self.initUI()
            self.pack()

        threading.Thread(target=self.update).start()

    def initUI(self):
        if self.font is None:
            self.font = tkFont.Font(family="Lucida Grande", size=self.fontsize)

        positionFrame = tk.Frame(master=self, bg=self.bg)  # , bg='red')
        positionFrame.pack(side=tk.LEFT)

        self.temperatureLabel = tk.Label(positionFrame, text="--° --%", font=self.font, anchor=tk.W, fg=self.fg, bg=self.bg)
        self.temperatureLabel.pack(side=tk.TOP, fill=tk.X)

    def updateGUI(self):
        if self.temperature is not None and self.temperatureLabel is not None:
            self.temperatureLabel['text'] = "{:.1f}° {:.0f}%".format(self.temperature, self.humidity)
            
    def update(self):
        # wait for main-thread
        time.sleep(self.startuptime)
        if self.mac is not None:
            logging.debug("{}".format(self.mac))
            dev = None
            while(True):
                try:
                    if dev is None:
                        logging.debug("connect to device:" + self.mac)
                        dev = btle.Peripheral(self.mac, addrType=btle.ADDR_TYPE_PUBLIC)
                                        
                    readings = dev.readCharacteristic(0x24)
                    logging.debug("{}".format(readings))
                    readings = dev.readCharacteristic(0x26)
                    logging.debug("{}".format(readings))

                    # self.battery = poller.parameter_value(MI_BATTERY)
                    # self.temperature = poller.parameter_value(MI_TEMPERATURE)
                    # self.humidity = poller.parameter_value(MI_HUMIDITY)
                    # logging.debug("{:.1f}° {:.0f}% {}".format(self.temperature, self.humidity, self.battery))
                    # self.updateGUI()
                except btle.BTLEDisconnectError as e:
                    logging.info("device not found {}".format(self.address))
                except:
                    logging.error(sys.exc_info(), exc_info=True)
                    self.temperature = None
                    self.humidity = None
                    self.battery = None
                    dev = None
                time.sleep(self.updatetime)
                
    def toJSON(self, prefix="inkbirdth2"):
        json = ""
        prefixText = ""
        if prefix is not None:
            prefixText = prefix + "_"
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
       

def main():
    if False:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s')

        root = tk.Tk()
        app = InkbirdTH2(master=root, mac="49:42:07:00:21:a8")
        root.mainloop()


if __name__ == '__main__':
    main()
