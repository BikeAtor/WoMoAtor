import sys
import logging
from .sensortype import SensorType
from .sensor import Sensor
from .sensor import SensorAzarton
from .sensor import SensorBrifit
from .sensor import SensorGovee
from .sensor import SensorInkbird

try:
    from .sensorgui import SensorGUI
except:
    pass
try:
    from .misensorbluepy import MiSensorBluepy
except:
    pass
try:
    from .misensorbleak import MiSensorBleak
except:
    pass
try:
    from .azartonsensor import AzartonSensor
except:
    pass
try:
    from .azartongui import AzartonGUI
except:
    pass
try:
    from .migui import MiGUI
except:
    pass
try:
    from .inkbirdth2 import InkbirdTH2
except:
    pass
# try:
#    from .bluetoothtemperaturesensor import BluetoothTemperatureSensor
# except:
#    pass
try:
    from .blescannerbluepy import BluetoothScannerBluepy
    logging.warning("no BluetoothScannerBluepy")
    logging.warning(sys.exc_info())
except:
    pass
try:
    from .blescannerbleak import BluetoothScannerBleak
    logging.warning("no BluetoothScannerBleak")
    logging.warning(sys.exc_info())
except:
    pass
