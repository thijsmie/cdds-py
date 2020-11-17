import ctypes as ct
from ctypes.util import find_library

library = find_library("ddsc")
dll = ct.CDLL(library)

class Entity:
    dll_handle = dll
       
        

