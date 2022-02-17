#!/usr/bin/env python3

import sys
sys.path.append('lib')

import os
import logging
import threading
import subprocess
import time
import json
import traceback
# GUI
import tkinter as tk
import tkinter.font as tkFont
import cairosvg
import io
from PIL import Image, ImageTk


class TPMSData:
    id = None
    pressure = None
    temperature = None
    lastTimeS = None
    
    def __init__(self,
                 pressure=None,
                 temperature=None,
                 lastTimeS=None):
        self.pressure = pressure
        self.temperature = temperature
        self.lastTimeS = lastTimeS

    
class TPMSGui(tk.Canvas):
    process = None
    sensor = None
    fontsize = 20
    font = None
    updatetime = 60
    lastupdate = time.time()
    frequency = None
    sensorFrontLeft = TPMSData()
    sensorFrontRight = TPMSData()
    sensorBackLeft = TPMSData()
    sensorBackRight = TPMSData()
    timeout = 5
    minpressure = 3.9
    dataFilename = None
    iconFilename = None
    carImage = None
    fg = "black"
    fgError = "red"
    bg = "white"

    def __init__(self, jsonConfig=None, master=None, frequency=434000000, size=(500, 500),
                 timeout=5, fontsize=20, updatetime=60,
                 dataFilename=None, iconFilename=None,
                 font=None, bg=None, fg=None, fgError=None, minpressure=None):
        self.fontsize = fontsize
        self.updatetime = updatetime
        # calculate self.font = font
        self.frequency = frequency
        self.timeout = timeout
        self.size = size
        if fg is not None:
            self.fg = fg
        if fgError is not None:
            self.fgError = fgError
        if bg is not None:
            self.bg = bg
        if minpressure is not None:
            self.minpressure = minpressure
        self.dataFilename = dataFilename
        self.iconFilename = iconFilename
        if master is not None:
            # No bin/x11    
            tk.Canvas.__init__(self, master, width=size[0], height=size[1], bg=self.bg)
            self.initUI()
            self.pack()

        self.fromJSONConfig(jsonConfig)
        self.loadData()

        threading.Thread(target=self.update).start()
        
    def initUI(self):
        self.initUIGraphic()

    def initUIGraphic(self):
        try:
            # try:
            #    1 + "1"
            # except:
            #    logging.warning(sys.exc_info(), exc_info=True)
            self.delete("all")
            imgageWidth = int(self.size[0])
            if self.font is None:
                self.font = tkFont.Font(family="Monospace", size=int(self.size[1] / 20), weight="bold")

            fontHeight = self.font.metrics('linespace')
            # clear
            self.create_rectangle(0, 0, self.size[0], self.size[1], fill=self.bg)
            # car
            if self.carImage is None and self.iconFilename:
                try:
                    image = Image.open(self.iconFilename)
                    image = image.resize((imgageWidth, imgageWidth), Image.ANTIALIAS)
                    self.carImage = ImageTk.PhotoImage(image)
                except:
                    logging.warning(sys.exc_info())   
            if self.carImage is not None:
                self.create_image((self.size[0] / 2, self.size[1] / 2), anchor=tk.CENTER, image=self.carImage)
            
            self.create_text(self.size[0] / 2, 0, anchor=tk.N, font=self.font, text="hPa")
            
            # oldest time sensor seen
            lastTimeS = 0.0
            try:
                sensor = self.sensorBackRight
                if sensor is not None and sensor.pressure is not None:
                    if sensor.lastTimeS is not None:
                        if sensor.lastTimeS < lastTimeS or lastTimeS < 1.0:
                            lastTimeS = sensor.lastTimeS
                        color = self.fg
                        if sensor.pressure < self.minpressure:
                            color = self.fgError
                        self.create_text(0, self.size[1] / 2 + imgageWidth / 2, anchor=tk.W, font=self.font, text=" {:.1f}".format(sensor.pressure), fill=color)
                    if sensor.temperature is not None:
                        self.create_text(0, self.size[1] / 2 + imgageWidth / 2 + fontHeight, anchor=tk.W, font=self.font, text=" {:2.0f}°".format(sensor.temperature), fill=color)
                else:
                    self.create_text(0, self.size[1] / 2 + imgageWidth / 2, anchor=tk.W, font=self.font, text=" -.-")
                    self.create_text(0, self.size[1] / 2 + imgageWidth / 2 + fontHeight, anchor=tk.W, font=self.font, text=" --°")
            except:
                logging.warning(sys.exc_info(), exc_info=True)
            
            try: 
                sensor = self.sensorBackLeft
                if sensor is not None and sensor.pressure is not None:
                    if sensor.lastTimeS is not None:
                        if sensor.lastTimeS < lastTimeS or lastTimeS < 1.0:
                            lastTimeS = sensor.lastTimeS
                    color = self.fg
                    if sensor.pressure < self.minpressure:
                        color = self.fgError
                    self.create_text(0, self.size[1] / 2 - imgageWidth / 2, anchor=tk.W, font=self.font, text=" {:.1f}".format(sensor.pressure), fill=color)
                    if sensor.temperature is not None:
                        self.create_text(0, self.size[1] / 2 - imgageWidth / 2 - fontHeight, anchor=tk.W, font=self.font, text=" {:2.0f}°".format(sensor.temperature), fill=color)
                else:
                    self.create_text(0, self.size[1] / 2 - imgageWidth / 2, anchor=tk.W, font=self.font, text=" -.-")
                    self.create_text(0, self.size[1] / 2 - imgageWidth / 2 - fontHeight, anchor=tk.W, font=self.font, text=" --°")
            except:
                logging.warning(sys.exc_info(), exc_info=True)
                
            try:
                sensor = self.sensorFrontLeft
                if sensor is not None and sensor.pressure is not None:
                    if sensor.lastTimeS is not None:
                        if sensor.lastTimeS < lastTimeS or lastTimeS < 1.0:
                            lastTimeS = sensor.lastTimeS
                    color = self.fg
                    if sensor.pressure < self.minpressure:
                        color = self.fgError
                    self.create_text(self.size[0], self.size[1] / 2 - imgageWidth / 2, anchor=tk.E, font=self.font, text="{:.1f} ".format(sensor.pressure), fill=color)
                    if sensor.temperature is not None:
                        self.create_text(self.size[0], self.size[1] / 2 - imgageWidth / 2 - fontHeight, anchor=tk.E, font=self.font, text="{:2.0f}° ".format(sensor.temperature), fill=color)
                else:
                    self.create_text(self.size[0], self.size[1] / 2 - imgageWidth / 2, anchor=tk.E, font=self.font, text="-.- ")
                    self.create_text(self.size[0], self.size[1] / 2 - imgageWidth / 2 - fontHeight, anchor=tk.E, font=self.font, text="--°")
            except:
                logging.warning(sys.exc_info(), exc_info=True)
                
            try:
                sensor = self.sensorFrontRight
                if sensor is not None and sensor.pressure is not None:
                    if sensor.lastTimeS is not None:
                        if sensor.lastTimeS < lastTimeS or lastTimeS < 1.0:
                            lastTimeS = sensor.lastTimeS
                    color = self.fg
                    if sensor.pressure < self.minpressure:
                        color = self.fgError
                    self.create_text(self.size[0], self.size[1] / 2 + imgageWidth / 2, anchor=tk.E, font=self.font, text="{:.1f} ".format(sensor.pressure), fill=color)
                    if sensor.temperature is not None:
                        self.create_text(self.size[0], self.size[1] / 2 + imgageWidth / 2 + fontHeight, anchor=tk.E, font=self.font, text="{:2.0f}° ".format(sensor.temperature), fill=color)
                else:
                    self.create_text(self.size[0], self.size[1] / 2 + imgageWidth / 2, anchor=tk.E, font=self.font, text="-.- ")
                    self.create_text(self.size[0], self.size[1] / 2 + imgageWidth / 2 + fontHeight, anchor=tk.E, font=self.font, text="--°")
            except:
                logging.warning(sys.exc_info(), exc_info=True)
                
            try:
                if lastTimeS is not None and lastTimeS > 1.0:
                    hours = int((time.time() - lastTimeS) / (60 * 60))
                    self.create_text(self.size[0] / 2, fontHeight, anchor=tk.N, font=self.font, text="{}Std".format(hours), fill=color)
                else:
                    self.create_text(self.size[0] / 2, fontHeight, anchor=tk.N, font=self.font, text="--")
            except:
                logging.warning(sys.exc_info(), exc_info=True)
                
            logging.debug("gui created")
        except:
            logging.warning(sys.exc_info(), exc_info=True)
            
    def updateGUI(self):
        try:
            logging.info("updateGUI")
            self.initUI()            
        except:
            logging.info(sys.exc_info(), exc_info=True)

    def update(self):
        if self.frequency is not None:
                # while (True):
                try:
                    logging.info("open: " + str(self.frequency))
                    # rtl_433 -f 43400000
                    self.process = subprocess.Popen(['rtl_433', '-f ' + str(self.frequency)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    # output, error_output = self.process.communicate()
                    # self.process = subprocess.Popen(['ls'], stdout=subprocess.PIPE)
                    # self.process = os.popen('rtl_433 -f ' + str(self.frequency))
                    if True:
                        threading.Thread(target=self.parseStream, args=(self.process.stdout, "stdout")).start()
                        threading.Thread(target=self.parseStream, args=(self.process.stderr, "stderr")).start()
                    else:
                        while(True):
                            if True:
                                self.parseLine(self.process.stderr.readline(), type="stderr")
                            
                            self.parseLine(self.process.stdout.readline())
                                   
                except:
                    logging.warning(sys.exc_info(), exc_info=True)
                    time.sleep(10)
        else:
            logging.info("no frequency")
    
    def parseStream(self, out, type="stdout"):
        logging.info("start parsing " + type)
        for line in out:
            self.parseLine(line, type);
        
    def parseLine(self, lineRaw, type="stdout"):
        try:
            if lineRaw is None or len(lineRaw) == 0:
                time.sleep(1)
                return
            line = None
            # logging.info(str(len(lineRaw)))
            if True:
                values = bytearray(lineRaw)
                            
                for x in range(len(values)):
                    if values[x] > 127:
                        values[x] = 32
                line = values.decode("ASCII")
                # line = lineRaw.decode("utf-8")
            else:
                line = lineRaw
                
            if line is not None: 
                # logging.info(line)
                line = line.strip()
                line = line.replace('\t', '')
                line = line.replace('\n', ' ')
                line = line.replace('  ', ' ')
                line = line.replace('  ', ' ')
                line = line.replace('  ', ' ')
                line = line.replace('  ', ' ')
                if len(line) == 0:
                    logging.debug("no data: " + line)
                else:
                    logging.info("tpms: " + type + " " + line)
                    if line == "No supported devices found.":
                        logging.info("no device found")
                        self.stop()
                    data = line.split(' ')
                    for pos in range(len(data)):
                        if data[pos] == '_':
                            self.sensor = None
                            break
                        if data[pos] == 'ID':
                            id = data[pos + 2]
                            logging.info("ID: " + id)
                            self.sensor = self.getSensor(str(id));
                        if self.sensor is not None:
                            if data[pos] == 'Pressure':
                                self.sensor.pressure = float(data[pos + 2]) / 100
                                self.sensor.lastTimeS = time.time()
                                logging.info("pressure:" + str(self.sensor.pressure))
                            if data[pos] == 'Temperature:':
                                self.sensor.temperature = float(data[pos + 1])
                                logging.info("temperature:" + str(self.sensor.temperature))
                            now = time.time()
                            if (now - self.lastupdate) > self.updatetime:
                                self.lastupdate = now
                            self.saveData()
                            self.updateGUI()
            else:
                time.sleep(1)
        except UnicodeDecodeError as e:
            logging.info("wrong line encoding");
            logging.info(lineRaw);
            logging.info(e, exc_info=True)
        except:
            # logging.info(line)
            logging.warning(sys.exc_info(), exc_info=True)
            time.sleep(1)

    def getSensor(self, id):
        if id == self.sensorFrontLeft.id:
            return self.sensorFrontLeft
        if id == self.sensorFrontRight.id:
            return self.sensorFrontRight
        if id == self.sensorBackLeft.id:
            return self.sensorBackLeft
        if id == self.sensorBackRight.id:
            return self.sensorBackRight
        logging.info("sensor not found: " + id + " - " + self.sensorFrontLeft.id + " " + self.sensorFrontRight.id + " " + self.sensorBackLeft.id + " " + self.sensorBackRight.id)
        return None
    
    def loadData(self):
        if self.dataFilename is not None and os.path.isfile(self.dataFilename):
            try:
                logging.info("load from file: {}".format(self.dataFilename))
                f = open(self.dataFilename, "r")
                count = 0
                while True:
                    count += 1
                    line = f.readline()
                    if not line:
                        break
                    line = line.strip()
                    logging.info("Line{}: {}".format(count, line))
                    if not line.startswith("#"):
                        values = line.split(" ")
                        if len(values) >= 4:
                            sensor = None
                            if values[0] == "FL:":
                                sensor = self.sensorFrontLeft
                            if values[0] == "FR:":
                                sensor = self.sensorFrontRight
                            if values[0] == "BL:":
                                sensor = self.sensorBackLeft
                            if values[0] == "BR:":
                                sensor = self.sensorBackRight
                                
                            if sensor is not None:
                                # sensor = TPMSData(pressure=float(values[1]),
                                #                                temperature=float(values[2]),
                                #                                lastTimeS=float(values[3]))
                                sensor.pressure = float(values[1])
                                sensor.temperature = float(values[2])
                                sensor.lastTimeS = float(values[3])
                                logging.info("found: {} {} {} {}".format(values[0], sensor.pressure, sensor.temperature, sensor.lastTimeS))
                            else:
                                logging.info("sensor not found: {}".format(line))
                f.close()
                self.updateGUI()
            except:
                logging.info(sys.exc_info(), exc_info=True)
    
    def saveData(self):
        if self.dataFilename is not None:
            try:
                logging.info("write to file: {}".format(self.dataFilename))
                f = open(self.dataFilename, "w")
                f.write("# {}\n".format(time.time()))
                sensor = self.sensorFrontLeft
                name = "FL"
                if sensor is not None and sensor.temperature is not None and sensor.pressure is not None and sensor.lastTimeS is not None:
                    f.write("{}: {} {} {}\n".format(name, sensor.pressure, sensor.temperature, sensor.lastTimeS))
                sensor = self.sensorFrontRight
                name = "FR"
                if sensor is not None and sensor.temperature is not None and sensor.pressure is not None and sensor.lastTimeS is not None:
                    f.write("{}: {} {} {}\n".format(name, sensor.pressure, sensor.temperature, sensor.lastTimeS))
                sensor = self.sensorBackLeft
                name = "BL"
                if sensor is not None and sensor.temperature is not None and sensor.pressure is not None and sensor.lastTimeS is not None:
                    f.write("{}: {} {} {}\n".format(name, sensor.pressure, sensor.temperature, sensor.lastTimeS))
                sensor = self.sensorBackRight
                name = "BR"
                if sensor is not None and sensor.temperature is not None and sensor.pressure is not None and sensor.lastTimeS is not None:
                    f.write("{}: {} {} {}\n".format(name, sensor.pressure, sensor.temperature, sensor.lastTimeS))
                f.close()
            except:
                logging.info(sys.exc_info(), exc_info=True)
    
    def stop(self):
        if self.process is not None:
            try:
                self.process.terminate()
                self.process.wait();
            except:
                logging.info(sys.exc_info(), exc_info=True)
                
    def fromJSONConfig(self, config):
        try:
            if config is not None:
                logging.info("parse JSON")
                if config.get("tpms"):
                    c = config["tpms"]
                else:
                    c = config
                if c.get("FL"):
                    s = c["FL"]
                    if s.get("id"):
                        self.sensorFrontLeft.id = str(s["id"])
                
                if c.get("FR"):
                    s = c["FR"]
                    if s.get("id"):
                        self.sensorFrontRight.id = str(s["id"])
                        
                if c.get("BL"):
                    s = c["BL"]
                    if s.get("id"):
                        self.sensorBackLeft.id = str(s["id"])
                
                if c.get("BR"):
                    s = c["BR"]
                    if s.get("id"):
                        self.sensorBackRight.id = str(s["id"])
                    
                if c.get("pressure_min"):
                    mp = c["pressure_min"]
                    self.minpressure = float(mp)
                    
                if c.get("icon_filename"):
                    v = c["icon_filename"]
                    self.iconFilename = str(v)
                    self.updateGUI()
        except:
            logging.info(sys.exc_info(), exc_info=True)
                    
    def toJSON(self, prefix="tpms"):
        json = ""
        prefixText = ""
        if prefix is not None:
            prefixText = prefix + "_"
        try:
            if self.sensorFrontLeft is not None:
                sensor = self.sensorFrontLeft
                if sensor.pressure is not None:
                    json += "\"" + prefixText + "front_left_pressure_kpa\": {}".format(sensor.pressure) + ",\n"
                if sensor.temperature is not None:
                    json += "\"" + prefixText + "front_left_temperature_c\": {}".format(sensor.temperature) + ",\n"

            if self.sensorFrontRight is not None:
                sensor = self.sensorFrontRight
                if sensor.pressure is not None:
                    json += "\"" + prefixText + "front_right_pressure_kpa\": {}".format(sensor.pressure) + ",\n"
                if sensor.temperature is not None:
                    json += "\"" + prefixText + "front_right_temperature_c\": {}".format(sensor.temperature) + ",\n"

            if self.sensorBackLeft is not None:
                sensor = self.sensorBackLeft
                if sensor.pressure is not None:
                    json += "\"" + prefixText + "back_left_pressure_kpa\": {}".format(sensor.pressure) + ",\n"
                if sensor.temperature is not None:
                    json += "\"" + prefixText + "back_left_temperature_c\": {}".format(sensor.temperature) + ",\n"

            if self.sensorBackRight is not None:
                sensor = self.sensorBackRight
                if sensor.pressure is not None:
                    json += "\"" + prefixText + "back_right_pressure_kpa\": {}".format(sensor.pressure) + ",\n"
                if sensor.temperature is not None:
                    json += "\"" + prefixText + "back_right_temperature_c\": {}".format(sensor.temperature) + ",\n"

        except:
            logging.warning(sys.exc_info(), exc_info=True)
        return json


def onClosingTPMS():
    root.destroy()
    os._exit(os.EX_OK)

        
def main():
    try:
        global root
        logging.basicConfig(level=logging.INFO, format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s')

        root = tk.Tk()
        fontMedium = tkFont.Font(family="TkFixedFont", size=14, weight="bold")
        root.protocol("WM_DELETE_WINDOW", onClosingTPMS)
        frame = tk.Frame(root)
        frame.pack(side=tk.TOP, fill=tk.X)
        
        configJSON = None
        filename = "../../config.json"
        if filename is not None and os.path.isfile(filename):
            configJSON = json.load(open(filename))
    
        # app = Victron(master=frame, port=None, font=fontMedium, size=(320, 320))
        app = TPMSGui(
                    # jsonConfig=configJSON,
                    iconFilename="../pic_free/question_pixabay_clone.png",
                    master=frame, frequency=434000000, size=(200, 380))
        app.sensorBackLeft.pressure = 1.4
        app.sensorFrontRight.pressure = 4.0
        app.updateGUI()
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
