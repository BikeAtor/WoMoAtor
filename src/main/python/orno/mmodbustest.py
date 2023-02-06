#!/usr/bin/env python3

import minimalmodbus

instrument = minimalmodbus.Instrument('/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A10MMQNK-if00-port0', 1)  # port name, slave address (in decimal)
instrument.mode = minimalmodbus.MODE_RTU
instrument.serial.baudrate = 9600
instrument.serial.bytesize = 8
instrument.serial.parity = minimalmodbus.serial.PARITY_EVEN
instrument.serial.stopbits = 1
instrument.serial.timeout = 3  
            
# instrument.read_float(20, 3, 2, 0)
print("from 272 (ID)")
x = instrument.read_float(272, 3, 2, 0)
print(x)
x = instrument.read_float(272, 3, 2, 1)
print(x)
x = instrument.read_long(272, 3, False, 0)
print(x)
x = instrument.read_long(272, 3, False, 1)
print(x)
print("")

print("from 273 (Baudrate)")
x = instrument.read_float(273, 3, 2, 0)
print(x)
x = instrument.read_float(273, 3, 2, 1)
print(x)
x = instrument.read_long(273, 3, False, 0)
print(x)
x = instrument.read_long(273, 3, False, 1)
print(x)
x = instrument.read_register(273, 0, 3, True)
print(x)
print("")

print("from 274 0x0112 (Display)")
# x = instrument.read_long(274, 3, False, 0)
# print(x)
# x = instrument.read_long(274, 3, False, 1)
# print(x)
x = instrument.read_register(274, 0, 3, False)
print(x)
print("")

print("from 305 0x131 (Voltage)")
# x = instrument.read_register(305, 0, 3, False)
# print(x)
x = instrument.read_register(305, 2, 3, True)
print(x)
print("")

print("from 313 0x0139 (Ampere)")
x = instrument.read_register(313, 3, 3, True)
print(x)
print("")

print("from 320 0x0140 (kW)")
x = instrument.read_register(320, 2, 3, True)
print(x)
# x = instrument.read_long(320, 3, False, 1)
# print(x)
print("")

print("from 40960 (Active Energy)")
x = instrument.read_long(40960, 3, False, 0)
print(x / 100)
# x = instrument.read_long(40960, 3, False, 1)
# print(x)
print("")
