#!/usr/bin/env python3

import sys
sys.path.append('..')

from abc import abstractmethod
import os
import logging
import threading
import time
import math

# GUI
import tkinter as tk
import tkinter.font as tkFont
import cairosvg
import io
from PIL import Image, ImageTk

import gasator


class GyroGUI(tk.Canvas):
    master = None
    
    sensor = None
    
    size = (500, 500)
    tireDistM = (5.0, 2.0)
    
    arrayX = []
    arrayY = []
    
    font = None
    fg = "black"
    bg = "white"
    verbose = False
    updateThread = None
    
    def __init__(self, master=None,
                size=(500, 500),
                # reifenabstand
                tireDistM=(5.0, 2.0),
                sensor=None,
                font=None,
                bg=None, fg=None,
                verbose=False):
        try:
            self.master = master
            self.sensor = sensor
            self.font = font
            if fg is not None:
                self.fg = fg
            if bg is not None:
                self.bg = bg
            self.verbose = verbose
            self.size = size
            self.tireDistM = tireDistM
            if self.font:
                logging.info("font: {}".format(self.font))
                newsize = self.font.actual("size") * 2
                if self.size:
                    newsize = min(newsize, self.size[0] / 15)
                newsize = int(newsize)
                self.font = tkFont.Font(family="Lucida Grande", size=newsize)
            if master is not None:
                tk.Canvas.__init__(self, master, width=size[0], height=size[1],
                                   # font=self.font,
                                   # fg=self.fg,
                                   bg=self.bg,
                                   borderwidth=0, highlightthickness=0)
                self.initUI()
                self.pack(fill=tk.BOTH)
                self.updateThread = threading.Thread(target=self.refreshGUI)
                self.updateThread.start()
            logging.info("initialized")
        except:
            logging.error(sys.exc_info(), exc_info=True)

    def refreshGUI(self):
        while True:
            self.initUI()
            time.sleep(1)
        
    def initUI(self):
        try:
            self.delete("all")
        except:
            logging.error(sys.exc_info(), exc_info=True)
        width = self.size[0]
        height = self.size[1]
        centerX = width / 2
        centerY = height / 2
        
        thickness = 5
        radiusMax = min(width / 2, height / 2) - thickness / 2
        radius = radiusMax
        self.create_oval(centerX - radius, centerY - radius, centerX + radius, centerY + radius,
                         width=thickness, fill="#55ff55", outline="black")
        
        radius = radiusMax / 4 * 3
        self.create_oval(centerX - radius, centerY - radius, centerX + radius, centerY + radius,
                         width=thickness, fill="#55ff55", outline="black")
        
        radius = radiusMax / 2
        self.create_oval(centerX - radius, centerY - radius, centerX + radius, centerY + radius,
                         width=thickness, fill="#55ff55", outline="black")
        
        radius = radiusMax / 4
        self.create_oval(centerX - radius, centerY - radius, centerX + radius, centerY + radius,
                         width=thickness, fill="#55ff55", outline="black")

        self.create_line(centerX, centerY - radiusMax, centerX, centerY + radiusMax,
                         width=thickness, fill="black")
        self.create_line(centerX - radiusMax, centerY , centerX + radiusMax, centerY ,
                         width=thickness, fill="black")

        if self.sensor:
            if self.sensor.gyroX and self.sensor.gyroY:
                factor = radiusMax / math.log(20.0)
                
                # change coordinate system
                gyroY = self.filterX(-self.sensor.gyroX + 2.3)  # - 2.5)
                gyroX = self.filterY(-self.sensor.gyroY - 0.2)  # + 1.6)
                
                logging.info("gyro: {:.2f} / {:.2f}".format(gyroX, gyroY))

                radius = max(10, self.size[0] / 20)
                x = centerX + factor * self.getLog(gyroX)
                y = centerY + factor * self.getLog(gyroY)
                self.create_oval(x - radius, y - radius, x + radius, y + radius,
                         width=2, fill="red", outline="black")
                
                if False:
                    gyroX = 0
                    gyroY = 0
                    x = centerX + factor * self.getLog(gyroX)
                    y = centerY + factor * self.getLog(gyroY)
                    self.create_oval(x - radius, y - radius, x + radius, y + radius,
                                    width=2, fill="#333333", outline="black")
                    
                if True:
                    text = "{:.1f}/{:.1f}".format(gyroX, gyroY)
                    self.create_text(width / 2, 0,
                                    anchor=tk.N, justify=tk.CENTER,
                                    fill="grey",
                                    font=self.font,
                                    text=text)
                    
                if True:
                    diff = self.getDiffCm(gyroX, gyroY, 0)
                    text = "{}cm".format(int(diff))
                    self.create_text(0, 0,
                                    anchor=tk.NW, justify=tk.LEFT,
                                    fill=self.fg,
                                    font=self.font,
                                    text=text)
                    
                    diff = self.getDiffCm(gyroX, gyroY, 1)
                    text = "{}cm".format(int(diff))
                    self.create_text(width, 0,
                                    anchor=tk.NE, justify=tk.RIGHT,
                                    fill=self.fg,
                                    font=self.font,
                                    text=text)
                    
                    diff = self.getDiffCm(gyroX, gyroY, 2)
                    text = "{}cm".format(int(diff))
                    self.create_text(0, height,
                                    anchor=tk.SW, justify=tk.LEFT,
                                    fill=self.fg,
                                    font=self.font,
                                    text=text)
                    
                    diff = self.getDiffCm(gyroX, gyroY, 3)
                    text = "{}cm".format(int(diff))
                    self.create_text(width, height,
                                    anchor=tk.SE, justify=tk.RIGHT,
                                    fill=self.fg,
                                    font=self.font,
                                    text=text)

    def filterX(self, gyroX):
        if len(self.arrayX) >= 6:
            for i in range(1, len(self.arrayX)):
                self.arrayX[i - 1] = self.arrayX[i]
            self.arrayX[len(self.arrayX) - 1] = gyroX
        else:
            self.arrayX.append(gyroX)
        
        sum = 0
        for i in range(0, len(self.arrayX)):
            sum += self.arrayX[i]
        return sum / len(self.arrayX)
    
    def filterY(self, gyroY):
        if len(self.arrayY) >= 6:
            for i in range(1, len(self.arrayY)):
                self.arrayY[i - 1] = self.arrayY[i]
            self.arrayY[len(self.arrayY) - 1] = gyroY
        else:
            self.arrayY.append(gyroY)
        
        sum = 0
        for i in range(0, len(self.arrayY)):
            sum += self.arrayY[i]
        return sum / len(self.arrayY)
        
    def getDiffCm(self, gyroX, gyroY, tire):
        diff = 0
        # logging.info("tan: {} {}".format(gyroX, math.tan(gyroX * math.pi / 180.0)))
        diffX = math.tan(abs(gyroX) * math.pi / 180.0) * 100.0 * self.tireDistM[1];
        diffY = math.tan(abs(gyroY) * math.pi / 180.0) * 100.0 * self.tireDistM[0];
        if tire == 0:
            # fronleft
            if gyroX >= 0 and gyroY >= 0:
                return diffX + diffY
            if gyroX < 0 and gyroY >= 0:
                return diffY
            if gyroX >= 0 and gyroY < 0:
                return diffX
            if gyroX < 0 and gyroY < 0:
                return 0
        elif tire == 1:
            # frontright
            if gyroX >= 0 and gyroY >= 0:
                return diffY
            if gyroX < 0 and gyroY >= 0:
                return diffX + diffY
            if gyroX >= 0 and gyroY < 0:
                return 0
            if gyroX < 0 and gyroY < 0:
                return diffX
        elif tire == 2:
            # backleft
            if gyroX >= 0 and gyroY >= 0:
                return diffX
            if gyroX < 0 and gyroY >= 0:
                return 0
            if gyroX >= 0 and gyroY < 0:
                return diffX + diffY
            if gyroX < 0 and gyroY < 0:
                return diffY
        elif tire == 3:
            # frontright
            if gyroX >= 0 and gyroY >= 0:
                return 0
            if gyroX < 0 and gyroY >= 0:
                return diffX
            if gyroX >= 0 and gyroY < 0:
                return diffY
            if gyroX < 0 and gyroY < 0:
                return diffX + diffY
            
        return diff
                   
    def getLog(self, number):
        if number > 0:
            return math.log(number + 1)
        return -math.log(abs(number) + 1)

           
def onClosingGUI():
    root.destroy()
    os._exit(os.EX_OK)

              
def main():
    try:
        global root
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s')

        root = tk.Tk()
        fontMedium = tkFont.Font(family="TkFixedFont", size=14, weight="bold")
        logging.info("font: {}".format(fontMedium))
        root.protocol("WM_DELETE_WINDOW", onClosingGUI)
        frame = tk.Frame(root)
        frame.pack(side=tk.TOP, fill=tk.X)
        
        sensor = gasator.GasLevelSerial();
        sensor.gyroX = 3
        sensor.gyroY = -3
    
        app = GyroGUI(master=frame,
                    sensor=sensor,
                    size=(200, 200),
                    fg="black",
                    font=fontMedium,
                    verbose=False)
        logging.info("mainloop")
        root.mainloop()
        logging.info("after mainloop")
        while(True):
            time.sleep(10000)
    except:
        logging.info(sys.exc_info(), exc_info=True)


if __name__ == '__main__':
    main()
