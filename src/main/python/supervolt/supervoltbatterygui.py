#!/usr/bin/env python3

import sys
sys.path.append('..')

import os
# for pyinstaller
dllpath = os.path.dirname(os.path.realpath(sys.argv[0]))
if dllpath not in os.environ:
    os.environ["PATH"] += os.pathsep + dllpath
import logging
import threading
import time
# import supervolt.supervoltbattery
try:
    from supervolt import supervoltbatterybluepy
except:
    logging.warning("no bluepy")
    pass
try:
    from supervolt import supervoltbatterybleak
except:
    logging.warning("no bleak")
    pass
# GUI
import tkinter as tk
import tkinter.font as tkFont
import cairo
import cairosvg
import io
from PIL import Image, ImageTk


class SupervoltBatteryGUI(tk.Canvas):
    fontsize = 20
    font = None
    fontSmall = None
    mac = None
    battery = None
    batteryImage = None
    batteryTextId = None
    batteryCellTextId = None
    loadImage = None
    loadTextId = None
    gui = "text"  # text or graphic
    orientation = "vertical"
    fg = "black"
    bg = "white"
    iconBattery = None
    iconLoad = None
    verbose = False
    showCellVoltage = True
    showCapacity = True
    disconnectAfterData = False
    updatetimeS = 60
    useBleak = False

    def __init__(self, master=None, mac=None, size=(500, 500),
                  gui="graphic", orientation="vertical",
                  iconBattery="pic_free/battery_pixabay_clone.png",
                  iconLoad="pic_free/bulb_pixabay_clone.png",
                  showCellVoltage=True,
                  showCapacity=True,
                  disconnectAfterData=False,
                  timeout=5, fontsize=20, updatetimeS=10,
                  font=None, fontSmall=None, bg=None, fg=None,
                  verbose=False,
                  useBleak=False):
        try:
            self.fontsize = fontsize
            self.font = font
            self.fontSmall = fontSmall
            # calculate self.font = font
            self.mac = mac
            self.iconBattery = iconBattery
            self.iconLoad = iconLoad
            self.showCellVoltage = showCellVoltage
            self.showCapacity = showCapacity
            self.disconnectAfterData = disconnectAfterData
            self.timeout = timeout
            self.gui = gui
            self.orientation = orientation
            self.size = size
            self.verbose = verbose
            if fg is not None:
                self.fg = fg
            if bg is not None:
                self.bg = bg
            if master is not None:
                tk.Canvas.__init__(self, master, width=size[0], height=size[1], bg=self.bg)
                self.initUI()
                self.pack()
                logging.info("before battery")
                if useBleak:
                    self.battery = supervoltbatterybleak.SupervoltBatteryBleak(mac=self.mac,
                                                                 verbose=self.verbose,
                                                                 updatetimeS=updatetimeS,
                                                                 callbackAfterData=self.updateGUI,
                                                                 disconnectAfterData=self.disconnectAfterData)
                else:
                    self.battery = supervoltbatterybluepy.SupervoltBatteryBluepy(mac=self.mac,
                                                                 verbose=self.verbose,
                                                                 updatetimeS=updatetimeS,
                                                                 callbackAfterData=self.updateGUI,
                                                                 disconnectAfterData=self.disconnectAfterData)
                self.battery.startReading()
                logging.info("after battery")
                threading.Thread(target=self.update).start()
            logging.info("initialized")
        except:
            logging.error(sys.exc_info(), exc_info=True)
        
    def initUI(self):
        # logging.info("visualisation: " + self.gui + " " + self.orientation)
        if self.gui == "text":
            self.initUIText()
        elif self.gui == "graphic":
            if self.font is None:
                self.font = tkFont.Font(family="Monospace", size=int(self.size[1] / 20), weight="bold")
            if self.fontSmall is None:
                self.fontSmall = tkFont.Font(family="Monospace", size=int(self.size[1] / 30), weight="normal")
                
            if self.orientation == "vertical":
                self.initUIGraphicVertical()
            else:
                self.initUIGraphicHorizontal()
        else:
            logging.warning("unknown visualisation: " + self.gui)

    def initUIGraphicHorizontal(self):
        try:
            factorx = int(self.size[0] / 2)
            factory = int(self.size[1] / 1)
            iconSize = int(min(factorx / 2, factory))
            x = 0
            # battery
            if self.batteryImage is None:
                image = Image.open(self.iconBattery)
                image = image.resize((iconSize, iconSize), Image.ANTIALIAS)
                self.batteryImage = ImageTk.PhotoImage(image) 
                batteryImageId = self.create_image((factorx * x, 0), anchor=tk.NW, image=self.batteryImage)
                self.tag_bind(batteryImageId, "<1>", self.batteryImageClicked)

            # self.create_rectangle(100, 100, 200, 130, fill="#aaaaaa", outline="grey60", alpha=.5)
            
            text = self.getBatteryText()
            if self.batteryTextId is None:
                self.batteryTextId = self.create_text(int(factorx * x + factorx), 0,
                                                        anchor=tk.NE, justify=tk.RIGHT,  #
                                                        fill=self.fg, font=self.font,
                                                        text=text)
            else:
                self.itemconfigure(self.batteryTextId, text=text)
            # width = self.font.measure(text)
            
            x += 1
            # load
            if self.loadImage is None:
                image = Image.open(self.iconLoad)
                image = image.resize((iconSize, iconSize), Image.ANTIALIAS)
                self.loadImage = ImageTk.PhotoImage(image) 
                self.create_image((factorx * x, 0), anchor=tk.NW, image=self.loadImage)
            
            text = self.getLoadText()
            if self.loadTextId is None:
                self.loadTextId = self.create_text(int(factorx * x + factorx), 0,
                                                    anchor=tk.NE, justify=tk.RIGHT,  #
                                                    fill=self.fg, font=self.font,
                                                    text=text)
            else:
                self.itemconfigure(self.loadTextId, text=text)
            
            text = ""
            if self.showCellVoltage:
                text += self.getBatteryCellText()
                
            if self.showCapacity:
                if len(text) > 0:
                    text += "\n"
                text += self.getBatteryCapacityText()

            if len(text) > 0:
                if self.batteryCellTextId is None:
                    self.batteryCellTextId = self.create_text(0, int(iconSize),
                                                              anchor=tk.NW, justify=tk.LEFT,  #
                                                              fill=self.fg, font=self.fontSmall,
                                                              text=text)
                else:
                    self.itemconfigure(self.batteryCellTextId, text=text)
        except:
            e = sys.exc_info()
            logging.info(e, exc_info=True)
            
    def initUIGraphicVertical(self):
        try:
            factory = int(self.size[1] / 2)
            factorx = int(self.size[0] / 3)
            iconSize = factorx
            y = 0
    
            # battery
            if self.batteryImage is None:
                image = Image.open(self.iconBattery)
                image = image.resize((iconSize, iconSize), Image.ANTIALIAS)
                self.batteryImage = ImageTk.PhotoImage(image) 
                batteryImageId = self.create_image((0, factory * y), anchor=tk.NW, image=self.batteryImage)
                self.tag_bind(batteryImageId, "<1>", self.batteryImageClicked)
                
            text = self.getBatteryText()
                
            if self.batteryTextId is None:
                self.batteryTextId = self.create_text(int(self.size[0]), int(factory * y),
                                                      anchor=tk.NE, justify=tk.RIGHT,  #
                                                      fill=self.fg, font=self.font,
                                                      text=text)
            else:
                self.itemconfigure(self.batteryTextId, text=text)
            # width = self.font.measure(text)
            
            text = ""
            if self.showCellVoltage:
                text += self.getBatteryCellText()
                
            if self.showCapacity:
                if len(text) > 0:
                    text += "\n"
                text += self.getBatteryCapacityText()

            if len(text) > 0:
                if self.batteryCellTextId is None:
                    self.batteryCellTextId = self.create_text(0, int(iconSize),
                                                              anchor=tk.SW, justify=tk.LEFT,  #
                                                              fill=self.fg, font=self.fontSmall,
                                                              text=text)
                else:
                    self.itemconfigure(self.batteryCellTextId, text=text)
            
            # logging.info("after battery")
            
            y = y + 1
            # load
            if self.loadImage is None:
                image = Image.open(self.iconLoad)
                image = image.resize((iconSize, iconSize), Image.ANTIALIAS)
                self.loadImage = ImageTk.PhotoImage(image) 
                self.create_image((0, factory * y), anchor=tk.NW, image=self.loadImage)
            
            text = self.getLoadText()
            if self.loadTextId is None:
                self.loadTextId = self.create_text(self.size[0], int(factory * y),
                                                   anchor=tk.NE, justify=tk.RIGHT,  #
                                                   fill=self.fg, font=self.font,
                                                   text=text)
            else:
                self.itemconfigure(self.loadTextId, text=text)

            # logging.info("gui created")
        except:
            logging.error(sys.exc_info(), exc_info=True)
    
    def getBatteryText(self):
        text = "--"
        try:
            if self.battery is not None:
                text = ""
                voltage = self.battery.totalV
                if voltage is None:
                    text += "- V\n"
                else:
                    text += "{:.2f} V\n".format(voltage)
                temp = self.battery.tempC[0]
                if temp is None:
                    text += "-°C\n"
                else:
                    text += "{:.0f}°C\n".format(temp)
                soc = self.battery.soc
                if soc is None:
                    text += "- %\n"
                else:
                    text += "{:.0f} %\n".format(soc)
                text += self.battery.getWorkingStateTextShort().replace(" ", "\n");
        except:
            logging.error(sys.exc_info(), exc_info=True)
            text = "error"
        return text
        
    def getBatteryCellText(self):
        textCell = ""
        try:
            if self.battery is not None:
                j = 0
                for i in range(0, 11):
                    if self.battery.cellV[i] is not None and self.battery.cellV[i] > 0:
                        logging.info("Cell {}: {}V".format(i, self.battery.cellV[i]))
                        j += 1
                        if len(textCell) > 0:
                            if j % 2 == 1:
                                textCell += "\n"
                            else:
                                textCell += " "
                        textCell += "{:.2f}V".format(self.battery.cellV[i])
        except:
            logging.error(sys.exc_info(), exc_info=True)
            textCell = "error"       
        return textCell
    
    def getBatteryCapacityText(self):
        textCapacity = ""
        try:
            if self.battery is not None:
                if self.battery.completeAh is not None and self.battery.remainingAh is not None:
                    textCapacity += "{:.0f}/{:.0f}Ah".format(self.battery.remainingAh, self.battery.completeAh)
        except:
            logging.error(sys.exc_info(), exc_info=True)
            textCapacity = "error"         
        return textCapacity
    
    def getLoadText(self):
        text = "--"
        try:
            if self.battery is not None:
                text = "- A\n- W"
                if self.battery.loadA is not None and self.battery.totalV is not None:
                    text = "{:.1f} A\n{:.1f} W".format(self.battery.loadA, (self.battery.loadA * self.battery.totalV))
        except:
            logging.error(sys.exc_info(), exc_info=True)
            text = "error"  
        return text
        
    def getBattery(self):
        return self.battery
    
    def initUIText(self):
        try:
            if self.font is None:
                self.font = tkFont.Font(family="Lucida Grande", size=self.fontsize)

            self.pack(side=tk.LEFT, fill=tk.X)

            # victronFrame = tk.Frame(master=self, bg=self.bg)  # , bg='red')
            # victronFrame.pack(side=tk.LEFT, fill=tk.X,)

            self.labelIn = tk.Label(self, text="--W --V", font=self.font, anchor=tk.W, fg=self.fg, bg=self.bg)
            self.labelIn.pack(side=tk.TOP, fill=tk.X, anchor=tk.NE)

            self.labelOut = tk.Label(self, text="--A --V", font=self.font, anchor=tk.W, fg=self.fg, bg=self.bg)
            self.labelOut.pack(side=tk.TOP, fill=tk.X, anchor=tk.NE)
            
            self.labelOther = tk.Label(self, text="--WM --Wh", font=self.font, anchor=tk.W, fg=self.fg, bg=self.bg)
            self.labelOther.pack(side=tk.TOP, fill=tk.X, anchor=tk.NE)
        except:
            logging.info(sys.exc_info(), exc_info=True)

    def updateGUI(self):
        try:
            logging.debug("updateGUI")
            if self.gui == "text":
                if self.labelOut is not None and self.outAmpere is not None and self.outVoltage is not None:
                    self.labelOut['text'] = "{:.1f}A {:.1f}V".format(self.outAmpere, self.outVoltage)
                if self.labelIn is not None and self.pvWatt is not None and self.pvVoltage is not None:
                    self.labelIn['text'] = "{}W {:.1f}V".format(self.pvWatt, self.pvVoltage)
                if self.labelOther is not None and self.pvWattDay is not None and self.pvWattMax is not None:
                    self.labelOther['text'] = "{}WM {}Wh".format(self.pvWattMax, self.pvWattDay)
            elif self.gui == "graphic":
                self.initUI()
            else:
                logging.warning("unknown visualisation: " + self.gui)
            
        except:
            logging.info(sys.exc_info(), exc_info=True)

    def update(self):
        while (True):
            try:
                time.sleep(self.updatetimeS)
                self.updateGUI()
            except:
                logging.error(sys.exc_info(), exc_info=True)
                time.sleep(self.updatetimeS)

    def batteryImageClicked(self, event):
        logging.info("clicked" + str(event))
        
    def toJSON(self, prefix="battery"):
        if self.battery is not None:
            return self.battery.toJSON(prefix)
        return ""
        

def onClosingSupervolt():
    root.destroy()
    os._exit(os.EX_OK)

        
def main():
    try:
        global root
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s')

        root = tk.Tk()
        fontMedium = tkFont.Font(family="TkFixedFont", size=14, weight="bold")
        root.protocol("WM_DELETE_WINDOW", onClosingSupervolt)
        frame = tk.Frame(root)
        frame.pack(side=tk.TOP, fill=tk.X)
    
        mac = "84:28:D7:8F:XX:XX"
        if len(sys.argv) > 1 and sys.argv[1]:
            mac = sys.argv[1]
        else:
            logging.warning("usage: supervoltbatterygui.py <BLE-Address>")
            return
        pathToIcons = "../pic_free"
        if not os.path.exists(pathToIcons):
            pathToIcons = "pic_free"
            if not os.path.exists(pathToIcons):
                logging.error("could not find icons")
        app = SupervoltBatteryGUI(master=frame, mac=mac,
                                  gui="graphic",
                                  orientation="vertical", size=(240, 320),
                                  # orientation="horizontal", size=(400, 100),
                                  iconBattery=pathToIcons + "/battery_pixabay_clone.png",
                                  iconLoad=pathToIcons + "/bulb_pixabay_clone.png",
                                  disconnectAfterData=True,
                                  updatetimeS=5,
                                  verbose=True,
                                  useBleak=True)
        logging.info("mainloop")
        root.mainloop()
        logging.info("after mainloop")
        while(True):
            time.sleep(10000)
    except:
        e = sys.exc_info()
        logging.info(e, exc_info=True)


if __name__ == '__main__':
    main()
