from pycdr import cdr
from pycdr.types import int8, int16, uint16, map, sequence, array


@cdr
class Test2:
    a: int8
    b: str
    v: uint16


@cdr
class Test:
    a: int8
    b: int16
    c: str
    d: bool
    e: float
    f: Test2
    k: sequence[int, 12]
    l: sequence[str]
    m: array[bool, 3]
    v: map[str, str]


a = Test(
    a = 1,
    b = 2,
    c = "blah",
    d = False,
    e = 0.2,
    f = Test2(a=12, b="wallallalla", v=12),
    k = [1,2,3],
    m = [True, True, False],
    l = [],
    v = {'a': 'b'}
)

data = a.serialize()
obj = Test.deserialize(data)

assert a == obj
print(obj)