import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pycdr.types import int8, int16, Len
from pycdr.serdata import cdr, serialize, deserialize
from typing import Annotated, List, Dict


@cdr
class Test2:
    a: int8
    b: str


@cdr
@keylist("a", "b", "f.a")
class Test:
    a: int8
    b: int16
    c: str
    d: bool
    e: float
    f: Test2
    k: Annotated[List[int], Len(3)]
    v: Dict[str, str]


a = Test(
    a = 1,
    b = 2,
    c = "blah",
    d = False,
    e = 0.2,
    f = Test2(a=12, b="wallallalla"),
    k = [1,2,3],
    v = {'a': 'b'}
)

data = a.encode()
obj = Test.decode(data)

assert a == obj
print(obj)