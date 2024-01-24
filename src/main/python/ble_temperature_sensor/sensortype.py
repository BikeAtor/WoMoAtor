#!/usr/bin/env python3

from enum import Enum


class SensorType(Enum):
    UNKNOWN = 1
    GOVEE = 1
    INKBIRD = 2
    BRIFIT = 3
    AZARTON = 4
    MI = 5
    SWITCHBOT = 6
