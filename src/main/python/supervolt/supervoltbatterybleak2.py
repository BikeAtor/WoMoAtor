#!/usr/bin/env python3

'''
connect to: 84:28:D7:8F:54:70
notificationhandler installed
services: 
Service <uuid=Generic Attribute handleStart=1 handleEnd=4>
Service <uuid=Generic Access handleStart=5 handleEnd=13>
Service <uuid=6e400001-b5a3-f393-e0a9-e50e24dcca9e handleStart=14 handleEnd=65535>

characteristics: 
Characteristic <Service Changed> uuid: 00002a05-0000-1000-8000-00805f9b34fb handle: 3 properties: INDICATE 
indicate enabled: 4
Characteristic <Device Name> uuid: 00002a00-0000-1000-8000-00805f9b34fb handle: 7 properties: READ 
length: 7 value: b'libatt\x00'
Characteristic <Appearance> uuid: 00002a01-0000-1000-8000-00805f9b34fb handle: 9 properties: READ 
length: 2 value: b'\x00\x00'
Characteristic <Peripheral Preferred Connection Parameters> uuid: 00002a04-0000-1000-8000-00805f9b34fb handle: 11 properties: READ 
length: 8 value: b'\x00\x00\x00\x00\x00\x00\x00\x00'
Characteristic <Central Address Resolution> uuid: 00002aa6-0000-1000-8000-00805f9b34fb handle: 13 properties: READ 
length: 1 value: b'\x00'
Characteristic <0002> uuid: 00000002-0000-1000-8000-00805f9b34fb handle: 16 properties: READ 
length: 2 value: b'\x01\x02'
Characteristic <6e400002-b5a3-f393-e0a9-e50e24dcca9e> uuid: 6e400002-b5a3-f393-e0a9-e50e24dcca9e handle: 19 properties: WRITE NO RESPONSE WRITE 
Characteristic <6e400003-b5a3-f393-e0a9-e50e24dcca9e> uuid: 6e400003-b5a3-f393-e0a9-e50e24dcca9e handle: 21 properties: NOTIFY 
send notify: desc: [<bluepy.btle.Descriptor object at 0xb655ae30>] handle[0]: 22
Characteristic <0001> uuid: 00000001-0000-1000-8000-00805f9b34fb handle: 24 properties: INDICATE 
indicate enabled: 25
'''
import sys
sys.path.append('..')
import os
os.environ['PATH'] = 'C:/msys64/mingw64/bin' + os.pathsep + os.environ['PATH']
import time
import atorlib
import threading
import logging
try:
    from supervolt.supervoltbatterydata import SupervoltBatteryData
except:
    logging.warning("no SupervoltBatteryData")
    pass


# read data from notification
class SupervoltBatteryBleak(atorlib.BleBleakBase):
    
    batteryData: SupervoltBatteryData = None
    
    def __init__(self,
                 adapter: int=0,
                 name=None,
                 mac=None,
                 data=None,
                 verbose=False,
                 updatetimeS=1,
                 timeout=None,
                 callbackAfterData=None,
                 disconnectAfterData=False):
        super().__init__(adapter=adapter, mac=mac, name=name, mtuSize=246,
                         timeout=timeout,
                         data=data, verbose=verbose, updatetimeS=updatetimeS, callbackAfterData=callbackAfterData,
                         disconnectAfterData=disconnectAfterData)
        self.batteryData = SupervoltBatteryData(verbose=verbose, updatetimeS=updatetimeS)
        if data:
            self.batteryData.parseData(data)
            
    async def enableNotifications(self):
        if False:
            data = b"\x02\x00"
            ret = await self.peripheral.writeCharacteristic(0x0004, data)
            if self.verbose:
                logging.info("0x0004: " + str(ret) + " " + str(data))
        data = b"\x01\x00"
        handle = 0x0015
        handle = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
        await self.device.start_notify(char_specifier=handle, callback=self.handleNotification)
        # ret = await self.peripheral.writeCharacteristic(0x0016, data)
        # if self.verbose:
        #    logging.info("0x0016: " + str(ret) + " " + str(data))
        if False:
            data = b"\x02\x00"
            ret = await self.peripheral.writeCharacteristic(0x0019, data)
            if self.verbose:
                logging.info("0x0019: " + str(ret) + " " + str(data))
        if self.verbose:
            logging.info("notifications enabled")
        
    def setData(self, data):
        if data:
            self.batteryData.parseData(data)
        
    # send request to battery for Realtime-Data
    async def requestRealtimeData(self):
        data = bytes(":000250000E03~", "ascii")
        handle = 0x0013
        handle = 19
        handle = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
        # 0x0013 -> 19 -> 6e400002-b5a3-f393-e0a9-e50e24dcca9e
        ret = await self.device.write_gatt_char(char_specifier=handle, data=data)
        # ret = self.device.writeCharacteristic(0x0013, data)
        if self.verbose:
            logging.debug(":000250000E03~: " + str(ret) + " " + str(data))
    
    # send request to battery for Capacity-Data
    async def requestCapacity(self):
        data = bytes(":001031000E05~", "ascii")
        handle = 0x0013
        handle = 19
        handle = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
        # 0x0013 -> 19 -> 6e400002-b5a3-f393-e0a9-e50e24dcca9e
        ret = await self.device.write_gatt_char(char_specifier=handle, data=data)
        if self.verbose:
            logging.debug(":001031000E05~: " + str(ret) + " " + str(data))
            
    async def requestData(self):
        dis = self.disconnectAfterData
        try:
            await self.enableNotifications()
            # disable, cause we will need two answers
            self.disconnectAfterData = False
            self.notificationReceived = False
            await self.requestRealtimeData()
            await self.waitForNotification(10.0)
            
            self.notificationReceived = False
            self.disconnectAfterData = dis
            await self.requestCapacity()
            await self.waitForNotification(10.0)
        except:
            logging.error(sys.exc_info(), exc_info=True)
            await self.disconnect()
        self.disconnectAfterData = dis
       
    def resetValues(self):
        try:
            self.batteryData.resetValues()
        except:
            logging.error(sys.exc_info(), exc_info=True)
    
    def getWorkingStateTextShort(self):
        if self.batteryData:
            return self.batteryData.getWorkingStateTextShort()
        return "Unbekannt"
        
    def getWorkingStateText(self):
        text = ""
        if self.batteryData is None:
            return "Unbekannt"
        return self.batteryData.getWorkingStateText();

    def appendState(self, text, append):
        if text is None  or len(text) == 0:
            return append
        return text + " | " + append
    
    def toJSON(self, prefix="battery"):
        if self.batteryData:
            return self.batteryData.toJSON(prefix=prefix)
        return ""
    
    def getData(self) -> SupervoltBatteryData:
        return self.batteryData


def main():
    try:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s')
        
        mac = "84:28:D7:8F:XX:XX"
        if len(sys.argv) > 1 and sys.argv[1] is not None:
            mac = sys.argv[1]
        else:
            logging.warning("usage: supervoltbatterybleak.py <BLE-Address>")
            return
        logging.info("connect to " + mac)
        battery = SupervoltBatteryBleak(mac=mac, name="SuperVoltTest", verbose=True, updatetimeS=10, disconnectAfterData=True)
        battery.startReading()
        while(True):
            time.sleep(10000)
    except:
        logging.error(sys.exc_info(), exc_info=True)


if __name__ == '__main__':
    main()
