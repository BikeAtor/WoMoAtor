#!/usr/bin/env python3

import sys
import logging
import PIL.Image
import PIL.ImageDraw
import PIL.ImageTk
# GUI
import tkinter as tk
import tkinter.font as tkFont
# OSM
import smopy
# GPS
import pynmea2


class GPSMap(tk.Frame):
    zoom = 13
    font = None
    spdLabel = None
    mapLabel = None
    lastGpsPosition = None
    fg = "black"
    bg = "white"
    defaultImagename = None
    defaultImage = None
    postition = None

    def __init__(self, master=None, position=None, font=None, bg=None, fg=None, defaultImagename=None, zoom=13):
        # super().__init__()
        self.font = font
        if fg is not None:
            self.fg = fg
        if bg is not None:
            self.bg = bg
        self.zoom = zoom
        self.defaultImagename = defaultImagename
        self.position = position
        tk.Frame.__init__(self, master, bg=self.bg)

        self.initUI()
        self.pack()
        if self.position:
            self.updateGUI(position=self.position)

    def initUI(self):
        try:
            if self.defaultImagename:
                image = PIL.Image.open(self.defaultImagename)
                self.defaultImage = PIL.ImageTk.PhotoImage(image)

            if self.font is None:
                self.font = tkFont.Font(family="Lucida Grande", size=20)

            positionFrame = tk.Frame(master=self, bg=self.bg)  # , bg='red')
            positionFrame.pack(side=tk.LEFT)

            frameValue = tk.Frame(positionFrame, bg=self.bg)
            frameValue.pack(side=tk.TOP, fill=tk.X)
            label = tk.Label(frameValue, text="Time:", font=self.font, fg=self.fg, bg=self.bg)
            label.pack(side=tk.LEFT)
            self.timeLabel = tk.Label(frameValue, text="", font=self.font, anchor=tk.W, fg=self.fg, bg=self.bg)
            self.timeLabel.pack(side=tk.RIGHT)

            frameValue = tk.Frame(positionFrame, bg=self.bg)
            frameValue.pack(side=tk.TOP, fill=tk.X)
            label = tk.Label(frameValue, text="Lat:", font=self.font, fg=self.fg, bg=self.bg)
            label.pack(side=tk.LEFT)
            self.latLabel = tk.Label(frameValue, text="", font=self.font, anchor=tk.W, fg=self.fg, bg=self.bg)
            self.latLabel.pack(side=tk.RIGHT)

            frameValue = tk.Frame(positionFrame, bg=self.bg)
            frameValue.pack(side=tk.TOP, fill=tk.X)
            label = tk.Label(frameValue, text="Lon:", font=self.font, fg=self.fg, bg=self.bg)
            label.pack(side=tk.LEFT)
            self.lonLabel = tk.Label(frameValue, text="", font=self.font, anchor=tk.W, fg=self.fg, bg=self.bg)
            self.lonLabel.pack(side=tk.RIGHT)

            frameValue = tk.Frame(positionFrame, bg=self.bg)
            frameValue.pack(side=tk.TOP, fill=tk.X)
            label = tk.Label(frameValue, text="Alt:", font=self.font, fg=self.fg, bg=self.bg)
            label.pack(side=tk.LEFT)
            self.altLabel = tk.Label(frameValue, text="", font=self.font, anchor=tk.W, fg=self.fg, bg=self.bg)
            self.altLabel.pack(side=tk.RIGHT)

            frameValue = tk.Frame(positionFrame, bg=self.bg)
            frameValue.pack(side=tk.TOP, fill=tk.X)
            label = tk.Label(frameValue, text="Sat:", font=self.font, fg=self.fg, bg=self.bg)
            label.pack(side=tk.LEFT)
            self.satLabel = tk.Label(frameValue, text="", font=self.font, anchor=tk.W, fg=self.fg, bg=self.bg)
            self.satLabel.pack(side=tk.RIGHT)

            # frameValue = tk.Frame( positionFrame )
            # frameValue.pack( side=tk.TOP, fill=tk.X )
            # label = tk.Label( frameValue, text = "Speed:", font=self.font )
            # label.pack( side=tk.LEFT )
            # self.spdLabel = tk.Label( frameValue, text="", font=self.font, anchor=tk.W )
            # self.spdLabel.pack( side=tk.RIGHT )

            self.mapLabel = tk.Label(self, image=self.defaultImage, fg=self.fg, bg=self.bg)
            self.mapLabel.pack(side=tk.LEFT)

            buttonFrame = tk.Frame(master=self, bg=self.bg)  # , bg='cyan')
            buttonFrame.pack(side=tk.LEFT)

            self.plusButton = tk.Button(buttonFrame, text="+", command=self.zoomIn, font=self.font, fg=self.fg, bg=self.bg)
            self.plusButton.pack(side=tk.TOP, fill=tk.X)

            self.zoomLabel = tk.Label(buttonFrame, text=str(self.zoom), font=self.font, fg=self.fg, bg=self.bg)
            self.zoomLabel.pack(side=tk.TOP, fill=tk.X)

            self.minusButton = tk.Button(buttonFrame, text="-", command=self.zoomOut, font=self.font, fg=self.fg, bg=self.bg)
            self.minusButton.pack(side=tk.TOP, fill=tk.X)

        except:
            e = sys.exc_info()
            logging.error(e, exc_info=True)
        logging.info("GUI created")

    def updateGUI(self, data=None, position=None, zoom=None):
        try:
            if self.mapLabel:
                if zoom:
                    self.zoom = zoom
                self.zoomLabel['text'] = str(self.zoom)
                if data is not None and data.gpsPosition is not None:
                    self.lastGpsPosition = data.gpsPosition
                if position is not None:
                    self.lastGpsPosition = position

                if self.lastGpsPosition is not None:
                    lat = self.lastGpsPosition.latitude
                    lon = self.lastGpsPosition.longitude
    
                    self.timeLabel['text'] = self.lastGpsPosition.timestamp.strftime('%H:%M:%S')
                    if lat is not None:
                        self.latLabel['text'] = "{:.4f}".format(lat)
                    if lon is not None:
                        self.lonLabel['text'] = "{:.4f}".format(lon)
                    if self.lastGpsPosition.altitude is not None:
                        self.altLabel['text'] = "{:.1f}".format(self.lastGpsPosition.altitude)
                    if self.lastGpsPosition.num_sats is not None:
                        self.satLabel['text'] = "{}".format(self.lastGpsPosition.num_sats)
                    if self.spdLabel is not None:
                        self.spdLabel['text'] = "{}".format(self.lastGpsPosition.geo_sep)

                    s = 0.000001
                    map = smopy.Map((lat - s, lon - s, lat + s, lon + s), z=self.zoom)
                    # show position
                    x, y = map.to_pixels(lat, lon)
                    # logging.info( "pos: " + str(x) + "/" + str(y) )
                    image = map.img
                    draw = PIL.ImageDraw.Draw(image)
                    r = 5
                    shape = [(x - r, y - r), (x + r, y + r)]
                    draw.ellipse(shape, fill="red", outline="black")
                    del draw

                    # logging.info( "size: " + str(image.size) )
                    image = image.resize((256, 256))
                    self.img = PIL.ImageTk.PhotoImage(image)
                    self.mapLabel['image'] = self.img
                    self.mapLabel.pack()
                    logging.info("map updated")
                else:
                    self.mapLabel['image'] = self.defaultImage
                    self.mapLabel.pack()
        except:
            e = sys.exc_info()
            logging.error(e, exc_info=True)
        logging.debug("GUI updated")

    def zoomIn(self):
        self.zoom += 1
        if(self.zoom > 17):
            self.zoom = 17
        logging.info("zoom: " + str(self.zoom))
        self.updateGUI()

    def zoomOut(self):
        self.zoom -= 1
        if(self.zoom < 0):
            self.zoom = 0
        logging.info("zoom: " + str(self.zoom))
        self.updateGUI()


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s')

    root = tk.Tk()
    app = GPSMap(master=root, defaultImagename="../pic_free/karte.png", zoom=5)
    gpsPosition = pynmea2.parse("$GPGGA,184353.07,1929.045,S,02410.506,E,1,04,2.6,100.00,M,-33.9,M,,0000*6D")
    app.updateGUI(position=gpsPosition)
    root.mainloop()


if __name__ == '__main__':
    main()

