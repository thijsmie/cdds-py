import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    ".."
)))

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    "../../idlpy/examples/helloworld/build/HelloWorldData"
)))

from Test import TestSimple, TestArray, TestSequence


with open("data_simple.bin", 'wb') as f:
    f.write(TestSimple(
        v1=1,
        v2="Hello World"
    ).encode())


with open("data_array.bin", 'wb') as f:
    f.write(TestArray(
        v1=[1, 2, 3]
    ).encode())


with open("data_sequence.bin", 'wb') as f:
    f.write(TestSequence(
        v1=[1, 2],
        v2=[1, 2, 3, 4, 5, 6]
    ).encode())
