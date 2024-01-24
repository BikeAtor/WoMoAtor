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
import cairosvg
import io
from PIL import Image, ImageTk


class GuiIconValue(tk.Canvas):
    master = None
    fontsize = 20
    font = None
    fontIconLabel = None
    name = None
    showName = True
    iconImage = None
    iconTextId = None
    valueTextId = None
    labelValue = None
    
    gui = "text"  # text or graphic
    orientation = "vertical"
    fg = "black"
    bg = "white"
    iconName = None
    verbose = False
    disconnectAfterData = False
    updatetimeS = 60

    def __init__(self, master=None, size=(500, 500),
                name=None, showName=True,
                gui="graphic", orientation="vertical",
                iconName="pic_free/question-pixabay_clone.png",
                disconnectAfterData=False,
                timeout=5, fontsize=20, updatetimeS=60,
                font=None, fontIconLabel=None,
                bg=None, fg=None,
                verbose=False):
        try:
            self.master = master
            self.fontsize = fontsize
            self.font = font
            self.fontIconLabel = fontIconLabel
            self.updatetimeS = updatetimeS
            # calculate self.font = font
            self.iconName = iconName
            self.disconnectAfterData = disconnectAfterData
            self.timeout = timeout
            self.gui = gui
            self.orientation = orientation
            self.size = size
            self.verbose = verbose
            self.name = name
            self.showName = showName
            if fg is not None:
                self.fg = fg
            if bg is not None:
                self.bg = bg
            if master is not None:
                tk.Canvas.__init__(self, master, width=size[0], height=size[1], bg=self.bg,
                                   borderwidth=0, highlightthickness=0)
                self.initUI()
                self.pack(fill=tk.BOTH)
            logging.info("initialized")
        except:
            logging.error(sys.exc_info(), exc_info=True)
            
    @abstractmethod
    def getText(self):
        return "?"
    
    @abstractmethod
    def toJSON(self, prefix="gas"):
        return ""
        
    def initUI(self):
        # logging.info("visualisation: " + self.gui + " " + self.orientation)
        if self.font is None and self.fontsize is not None:
            self.font = tkFont.Font(family="Monospace", size=self.fontsize, weight="bold")
        if self.fontIconLabel is None:
            self.fontIconLabel = self.font
        if self.gui == "text":
            self.initUIText()
        elif self.gui == "graphic":
            if self.orientation == "vertical":
                self.initUIGraphicVertical()
            else:
                self.initUIGraphicHorizontal()
            self.pack(fill=tk.BOTH)
        else:
            logging.warning("unknown visualisation: " + self.gui)

    def initUIGraphicHorizontal(self):
        try:
            if self.verbose:
                logging.info("{}/{}".format(self.size[0], self.size[1]))
            factorx = int(self.size[0] / 1)
            factory = int(self.size[1] / 1)
            iconSize = int(min(factorx / 2 , factory))
            x = 0
            # icon
            if self.iconImage is None:
                image = Image.open(self.iconName)
                # width, height = image.size
                # if width > height:
                #    iconSize *= height / width
                image = image.resize((iconSize, iconSize), Image.LANCZOS)
                self.iconImage = ImageTk.PhotoImage(image) 
                iconImageId = self.create_image((factorx * x, 0), anchor=tk.NW, image=self.iconImage)
                self.tag_bind(iconImageId, "<1>", self.iconImageClicked)

            text = self.getIconText()
            if text is not None:
                if self.iconTextId is None:
                    self.iconTextId = self.create_text(0, int(iconSize * 0.5),
                                                      anchor=tk.W, justify=tk.LEFT,  #
                                                      fill=self.fg, font=self.fontIconLabel,
                                                      text=text)
                else:
                    self.itemconfigure(self.iconTextId, text=text)

            text = self.getText()
            if self.valueTextId is None:
                self.valueTextId = self.create_text(int(factorx * x + factorx), iconSize * 0.5,
                                                        anchor=tk.E, justify=tk.RIGHT,  #
                                                        fill=self.fg, font=self.font,
                                                        text=text)
            else:
                self.itemconfigure(self.valueTextId, text=text)
            # width = self.font.measure(text)
            
        except:
            logging.info(sys.exc_info(), exc_info=True)
            
    def initUIGraphicVertical(self):
        try:
            # factory = int(self.size[1] / 2)
            factorx = int(self.size[0] / 3)
            factory = factorx
            iconSize = factorx
            y = 0
    
            # icon
            if self.iconImage is None:
                image = Image.open(self.iconName)
                image = image.resize((iconSize, iconSize), Image.LANCZOS)
                self.iconImage = ImageTk.PhotoImage(image) 
                iconImageId = self.create_image((0, factory * y), anchor=tk.NW, image=self.iconImage)
                self.tag_bind(iconImageId, "<1>", self.iconImageClicked)
            
            text = self.getIconText()
            if text is not None:
                if self.iconTextId is None:
                    self.iconTextId = self.create_text(0, int(factory * y + iconSize * 0.5),
                                                      anchor=tk.W, justify=tk.LEFT,  #
                                                      fill=self.fg, font=self.fontIconLabel,
                                                      text=text)
                else:
                    self.itemconfigure(self.iconTextId, text=text)

            text = self.getText()
            if self.valueTextId is None:
                self.valueTextId = self.create_text(int(self.size[0]), int(factory * y + iconSize * 0.5),
                                                      anchor=tk.E, justify=tk.RIGHT,  #
                                                      fill=self.fg, font=self.font,
                                                      text=text)
            else:
                self.itemconfigure(self.valueTextId, text=text)
            # width = self.font.measure(text)
            
            # logging.info("gui created")
        except:
            logging.error(sys.exc_info(), exc_info=True)
    
    def initUIText(self):
        try:
            if self.font is None:
                self.font = tkFont.Font(family="Lucida Grande", size=self.fontsize)

            self.pack(side=tk.LEFT, fill=tk.X)
            frame = tk.Frame(master=self, bg=self.bg)  # , bg='red')
            frame.pack(side=tk.TOP, fill=tk.X)
            if self.name is not None:
                label = tk.Label(frame, text=self.name + ":", font=self.font, bg=self.bg, fg=self.fg)
                label.pack(side=tk.LEFT)

            text = self.getText()
            self.labelValue = tk.Label(frame, text=text, font=self.font, anchor=tk.W, fg=self.fg, bg=self.bg)
            self.labelValue.pack(side=tk.RIGHT, fill=tk.X, anchor=tk.NE)
        except:
            logging.info(sys.exc_info(), exc_info=True)

    def updateGUI(self):
        try:
            if self.verbose:
                logging.info("updateGUI")
            if self.gui == "text":
                if self.labelValue is not None and self.getText() is not None:
                    self.labelValue['text'] = self.getText()
            elif self.gui == "graphic":
                self.initUI()
            else:
                logging.warning("unknown visualization: " + self.gui)
            
        except:
            logging.info(sys.exc_info(), exc_info=True)

    def getIconText(self):
        # logging.info("{} {}".format(self.name, self.showName))
        if self.name is not None and self.showName is not None and self.showName is True:
            return self.name
        return None
    
    def update(self):
        while (True):
            try:
                time.sleep(self.updatetimeS)
                self.updateGUI()
            except:
                logging.info(sys.exc_info(), exc_info=True)
                time.sleep(10)

    def iconImageClicked(self, event):
        logging.info("clicked" + str(event))

