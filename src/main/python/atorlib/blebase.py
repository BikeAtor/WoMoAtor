#!/usr/bin/env python3

import sys

from abc import abstractmethod
import time

import threading
import logging
import asyncio


# read data from notification
class BleBase():
    lock = threading.Lock()
    
    verbose = False
    mac = None
    name = None
    mtuSize = None
    disconnectAfterData = False;
    updatetimeS = 1
    callbackAfterData = None
    adapter:int = 0
    
    # time of data changed
    lastUpdatetime = time.time()
    # time of last call to resetValues
    lastResettime = time.time()
    maxtime = 70  # seconds
    
    useBleak = False
    
    def __init__(self,
                 adapter: int=0,
                 mac=None,
                 name=None,
                 mtuSize=None,
                 data=None,
                 verbose=False,
                 updatetimeS=1,
                 callbackAfterData=None,
                 disconnectAfterData=False,
                 useBleak=False):
        self.adapter = adapter
        self.verbose = verbose
        self.mac = mac
        self.name = name
        if self.name is None:
            self.name = "noname"
        self.mtuSize = mtuSize
        self.updatetimeS = updatetimeS
        self.maxtime = self.updatetimeS * 10
        self.callbackAfterData = callbackAfterData
        self.disconnectAfterData = disconnectAfterData
        self.useBleak = useBleak
        if data is not None:
            self.parseData(data)
        
    # send request to device for data
    @abstractmethod
    def requestData(self):
        raise NotImplementedError()
    
    # try to read values from data
    @abstractmethod
    def parseData(self, data):
        raise NotImplementedError()
    
    @abstractmethod
    def resetValues(self):
        raise NotImplementedError()
    
    @abstractmethod
    def connect(self):
        raise NotImplementedError()
    
    @abstractmethod
    def isConnected(self) -> bool:
        raise NotImplementedError()
    
    @abstractmethod
    def disconnect(self):
        raise NotImplementedError()
    
    @abstractmethod
    def requestOnce(self):
        raise NotImplementedError()
    
    def dataChanged(self, resetTime=True):
        if resetTime:
            self.lastUpdatetime = time.time()
            self.lastResettime = time.time()
        if self.callbackAfterData is not None:
            if self.verbose:
                logging.info("callbackAfterData")
            self.callbackAfterData()
    
    def checkAgeOfValues(self):
        if (time.time() - self.lastUpdatetime) > self.maxtime:
            # data is old
            if (time.time() - self.lastResettime) > self.maxtime:
                # last time for reset is also too old, so it will be called every maxtime
                self.lastResettime = time.time()
                logging.debug("reset values after time {}/{}".format(self.maxtime, (time.time() - self.lastUpdatetime)))
                self.resetValues()
                self.dataChanged(False)
          
    def startReading(self):
        if self.mac is not None:
            # start reading values
            threading.Thread(target=self.requestAlways).start()
            if not self.disconnectAfterData:
                threading.Thread(target=self.stayConnected).start()
        else:
            logging.warning("no mac given")
            
    def stayConnected(self):
        try:
            while True:
                try:
                    if not self.isConnected():
                        self.connect()
                except:
                    logging.error(sys.exc_info(), exc_info=True)
                
                time.sleep(10)
        except:
            logging.error(sys.exc_info(), exc_info=True)

    # set data
    def setData(self, data):
        self.parseData(data)
            
    def requestAlways(self):
        while True:
            try:
                if self.useBleak:
                    # time.sleep(3)
                    if sys.version_info >= (3, 7):
                        asyncio.run(self.requestAlwaysAsync())
                    else:
                        # futures = [self.requestAlwaysAsync]
                        # loop = asyncio.get_event_loop()
                        # loop.run_until_complete(asyncio.wait(futures))
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop = asyncio.get_event_loop()
                        loop.run_until_complete(self.requestAlwaysAsync())
                else:
                    self.requestAlwaysSync()
            except:
                logging.error(sys.exc_info(), exc_info=True)
                time.sleep(self.updatetimeS)
                
    def requestAlwaysSync(self):
        while True:
            try:
                self.requestOnce()
                # wait before for next request
                time.sleep(self.updatetimeS)
            except:
                logging.error(sys.exc_info(), exc_info=True)
                time.sleep(1)
                
    async def requestAlwaysAsync(self):
        while True:
            try:
                if self.verbose:
                    logging.debug("async: start request")
                await self.requestOnce()
                # wait before for next request
                time.sleep(self.updatetimeS)
            except:
                logging.error(sys.exc_info(), exc_info=True)
                time.sleep(1)
        
    def toJSON(self, prefix=None):
        return ""
    
    def setVerbose(self, value: str):
        if value:
            self.verbose = ("TRUE" == value.upper())
        logging.info("verbose: {}".format(self.verbose))
