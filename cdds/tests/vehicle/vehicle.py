from cdds.domain import DDSEntity
import os
from ctypes import c_char_p, c_int16


@DDSEntity("vehicle")
class Vehicle:
    name: c_char_p
    x: c_int16
    y: c_int16
