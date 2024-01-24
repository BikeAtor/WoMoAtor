#!/usr/bin/env python3

import sys
sys.path.append('..')

from abc import abstractmethod
import os
import logging
import threading
import time

# GUI
import tkinter as tk
import tkinter.font as tkFont
import tkinter.tix as tix
import cairosvg
import io
from PIL import Image, ImageTk

import tooltip

import atorlib


class GuiIconValueBattery(atorlib.GuiIconValue):
    balloon = None
    batteryImage = None
    batteryIconName1 = None
    batteryIconName2 = None
    batteryIconName3 = None
    batteryIconName4 = None

    def __init__(self, balloon=None,
                batteryIconName1=None,
                batteryIconName2=None,
                batteryIconName3=None,
                batteryIconName4=None,
                master=None, size=(500, 500),
                name=None, showName=True,
                gui="graphic", orientation="vertical",
                iconName="pic_free/question-pixabay_clone.png",
                disconnectAfterData=False,
                timeout=5, fontsize=20, updatetimeS=60,
                font=None, fontIconLabel=None,
                bg=None, fg=None,
                verbose=False):
        try:
            self.balloon = balloon
            self.batteryIconName1 = batteryIconName1
            self.batteryIconName2 = batteryIconName2
            self.batteryIconName3 = batteryIconName3
            self.batteryIconName4 = batteryIconName4
            super().__init__(master=master, size=size,
                  name=name, showName=showName,
                  gui=gui, orientation=orientation,
                  iconName=iconName,
                  disconnectAfterData=disconnectAfterData,
                  timeout=timeout, fontsize=fontsize, updatetimeS=updatetimeS,
                  font=font, fontIconLabel=fontIconLabel,
                  bg=bg, fg=fg,
                  verbose=verbose)
            self.setBalloonText()
        except:
            logging.error(sys.exc_info(), exc_info=True)
            
    def setBalloonText(self):
        try:
            if self.balloon is not None:
                bat = self.getBatteryLevel()
                batText = ""
                if bat is not None:
                    batText = "\nBat: {}%".format(int(bat))
                self.balloon.bind_widget(self, balloonmsg="{}{}".format(self.getText(), batText))
            else:
                if self.verbose:
                    logging.info("no balloon")
        except:
            logging.error(sys.exc_info(), exc_info=True)
        
    def initUIGraphicHorizontal(self):
        try:
            super().initUIGraphicHorizontal()

            factorx = int(self.size[0])
            factory = int(self.size[1])
            iconSize = int(max(factory / 3 , 25))
            x = 0
            # icon
            batteryLevel = self.getBatteryLevel()
            # logging.info("{}".format(batteryLevel))
            if batteryLevel:
                iconName = None
                if batteryLevel < 25:
                    iconName = self.batteryIconName1
                elif batteryLevel < 50:
                    iconName = self.batteryIconName2
                elif batteryLevel < 75:
                    iconName = self.batteryIconName3
                elif batteryLevel <= 100:
                    iconName = self.batteryIconName4
                else:
                    logging.info("unkown batteryLevel {}".format(batteryLevel))
                if iconName is not None:
                    image = Image.open(iconName)
                    image = image.resize((iconSize, iconSize), Image.LANCZOS)
                    self.batteryImage = ImageTk.PhotoImage(image) 
                    iconImageId = self.create_image((factorx * x, 0), anchor=tk.NW, image=self.batteryImage)
                    self.tag_bind(iconImageId, "<1>", self.iconImageClicked)
                    self.setBalloonText()
                else:
                    logging.info("no icon")
            else:
                if self.verbose:
                    logging.info("no battery")
            
        except:
            logging.info(sys.exc_info(), exc_info=True)
            
    def initUIGraphicVertical(self):
        try:
            super().initUIGraphicVertical()
            
            factorx = int(self.size[0] / 3)
            factory = factorx
            iconSize = int(max(factorx / 3, 25))
            y = 0
    
            # icon
            batteryLevel = self.getBatteryLevel()
            if batteryLevel is not None:
                iconName = None
                if batteryLevel < 25:
                    iconName = self.batteryIconName1
                elif batteryLevel < 50:
                    iconName = self.batteryIconName2
                elif batteryLevel < 75:
                    iconName = self.batteryIconName3
                elif batteryLevel <= 100:
                    iconName = self.batteryIconName4
                else:
                    logging.info("unkown batterLevel {}".format(batteryLevel))
                if iconName is not None:
                    image = Image.open(iconName)
                    image = image.resize((iconSize, iconSize), Image.LANCZOS)
                    self.batteryImage = ImageTk.PhotoImage(image) 
                    iconImageId = self.create_image((0, factory * y), anchor=tk.NW, image=self.batteryImage)
            else:
                logging.info("no battery")
            
        except:
            logging.error(sys.exc_info(), exc_info=True)
    
    @abstractmethod
    def getBatteryLevel(self):
        return None
