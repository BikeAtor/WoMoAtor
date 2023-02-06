#!/usr/bin/env python3

import sys
sys.path.append('..')
try:
    from abc import abstractmethod
    import time
    import atorlib
    import asyncio
    import bleak
    import threading
    import logging
except:
    print(sys.exc_info())
    

# read data from notification
class BleBleakBase(atorlib.BleBase):
    
    device: bleak.BleakClient = None
    
    notificationReceived = False
    
    sleepBetweenRequests = 5.0
    
    timeout: float = 30.0
    
    def __init__(self,
                 adapter:int=0,
                 mac=None,
                 name=None,
                 mtuSize=None,
                 data=None,
                 verbose=False,
                 updatetimeS=1,
                 timeout=None,
                 callbackAfterData=None,
                 disconnectAfterData=False):
        super().__init__(adapter=adapter, mac=mac, name=name, mtuSize=mtuSize,
                         data=data, verbose=verbose, updatetimeS=updatetimeS, callbackAfterData=callbackAfterData,
                         disconnectAfterData=disconnectAfterData,
                         useBleak=True);
        if timeout:
            self.timeout = timeout
    
    async def __enter__(self):
        await self.connect()
        return self

    async def __exit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    # receive notifications
    async def handleNotification(self, sender, data):
        if self.verbose:
            logging.info("notification: {} {}".format(data.hex(), sender))
        if data is not None:
            self.data = data
            self.parseData(data)
            self.lastUpdatetime = time.time()
            try:
                if self.callbackAfterData is not None:
                    if self.verbose:
                        logging.info("callbackAfterData")
                    self.callbackAfterData()
                if self.disconnectAfterData:
                    if self.verbose:
                        logging.info("disconnect")
                    await self.disconnect()
            except:
                logging.error(sys.exc_info(), exc_info=True)
        self.notificationReceived = True
        
    async def waitForNotification(self, timeS: float) -> bool:
        start = time.time()
        await asyncio.sleep(0.1)
        while(time.time() - start < timeS and not self.notificationReceived):
            await asyncio.sleep(0.1)
        if self.verbose:
            logging.debug("used: {}".format((time.time() - start)))
        return self.notificationReceived
            
    async def connect(self):
        try:
            if self.verbose:
                logging.info("wait for lock")
            with self.lock:
                if self.device is None:
                    logging.info("connect to: {} {} ({}) {}s".format(self.adapter, self.mac, self.name, self.timeout))
                    if True:
                        self.device = bleak.BleakClient(self.mac, timeout=self.timeout, adapter="hci{}".format(self.adapter))
                        if self.device:
                            await self.device.connect()
                            if self.verbose:
                                logging.info("connected: {}".format(self.device.is_connected))
                            if self.mtuSize is not None:
                                try:
                                    await self.device._acquire_mtu()
                                    logging.warning("bleak does not support MTU-Size: {}".format(self.device.mtu_size))
                                except:
                                    logging.error(sys.exc_info())
                            await self.requestOnce()
                    else:
                        with bleak.BleakClient(self.mac, timeout=20.0) as self.device:
                            if self.verbose:
                                logging.info("connected: {}".format(self.device.is_connected))
                            if self.mtuSize is not None:
                                logging.warning("bleak does not support MTU-Size")
                            self.requestOnce()
                else:
                    logging.info("already connected")
        except:
            await self.disconnect()
            self.checkAgeOfValues()
            logging.error(sys.exc_info())
            # logging.error(sys.exc_info(), exc_info=True)

    def isConnected(self) -> bool:
        return self.device is not None
    
    async def disconnect(self):
        try:
            if self.device:
                dev = self.device
                self.device = None
                logging.info("disconnect from: {}".format(self.mac))
                await dev.disconnect()
        except:
            logging.error(sys.exc_info(), exc_info=True)
        self.device = None
            
    async def requestOnce(self):
        if self.verbose:
            logging.info("requestOnce")
        try:
            if self.device is None:
               await self.connect()
            if self.device is not None:
                if self.verbose:
                    logging.info("requestData")
                dataReceived = False
                await self.requestData()
                time.sleep(self.sleepBetweenRequests)
                await self.disconnect()        
            else:
                if self.verbose:
                    logging.info("no device")
                time.sleep(self.updatetimeS)
        except:
            logging.error(sys.exc_info(), exc_info=True)
            self.disconnect()
            self.checkAgeOfValues()
            time.sleep(1)
        
