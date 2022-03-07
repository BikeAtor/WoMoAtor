#!/usr/bin/env python3

import sys
sys.path.append('..')
from abc import abstractmethod
import time
import atorlib
import bluepy.btle
import threading
import logging


# read data from notification
class BleBluepyBase(atorlib.BleBase):
    peripheral = None
    
    sleepBetweenRequests = 0.2

    def __init__(self,
                 mac=None,
                 name=None,
                 mtuSize=None,
                 data=None,
                 verbose=False,
                 updatetimeS=1,
                 callbackAfterData=None,
                 disconnectAfterData=False):
        super().__init__(mac=mac, name=name, mtuSize=mtuSize,
                         data=data, verbose=verbose, updatetimeS=updatetimeS, callbackAfterData=callbackAfterData,
                         disconnectAfterData=disconnectAfterData,
                         useBleak=False);
        bluepy.btle.DefaultDelegate.__init__(self)
        
    # receive notifications
    def handleNotification(self, cHandle, data):
        if data is not None:
            if self.verbose:
                logging.info("notification: {}".format(data))
            self.data = data
            self.parseData(data)
            self.lastUpdatetime = time.time()
            
    def connect(self):
        try:
            if self.verbose:
                logging.info("wait for lock")
            with self.lock:
                if self.peripheral is None:
                    logging.info("connect to: {} ({})".format(self.mac, self.name))
                    self.peripheral = bluepy.btle.Peripheral(deviceAddr=self.mac, iface=0)
                    if self.mtuSize is not None:
                        self.peripheral.setMTU(self.mtuSize)
                    self.peripheral.withDelegate(self)
                    if self.verbose:
                        logging.info("notificationhandler installed")
                else:
                    logging.info("already connected")
        except:
            self.disconnect()
            self.checkAgeOfValues()
            logging.error(sys.exc_info())
            # logging.error(sys.exc_info(), exc_info=True)

    def isConnected(self) -> bool:
        return self.peripheral is not None
    
    def disconnect(self):
        try:
            if self.peripheral:
                logging.info("disconnect from: {}".format(self.mac))
                self.peripheral.disconnect()
        except:
            logging.error(sys.exc_info(), exc_info=True)
        self.peripheral = None
            
    def requestOnce(self):
        if self.verbose:
            logging.info("requestOnce")
        try:
            if self.peripheral is None:
                self.connect()
            if self.peripheral is not None:
                
                if self.verbose:
                    logging.info("waitForNotifications")
                dataReceived = False
                self.requestData()
                if self.peripheral.waitForNotifications(10.0):
                    dataReceived = True
                    if self.verbose:
                        logging.info("notification received")
                    time.sleep(self.sleepBetweenRequests)
                if dataReceived and self.callbackAfterData is not None:
                    if self.verbose:
                        logging.info("callbackAfterData: " + str(dataReceived))
                    self.callbackAfterData()
                if self.disconnectAfterData:
                    if self.verbose:
                        logging.info("disconnect")
                    self.disconnect()
            else:
                if self.verbose:
                    logging.info("no peripheral")
                time.sleep(self.updatetimeS)
        except:
            logging.error(sys.exc_info(), exc_info=True)
            self.disconnect()
            self.checkAgeOfValues()
            time.sleep(1)
        
