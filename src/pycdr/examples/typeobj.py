from pycdr import cdr
from pycdr.types import int8, int16, uint16, map, sequence, array
from pycdr.type_object.builder import TypeObjectBuilder

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


t = TypeObjectBuilder()
print(t.to_typeobject(Test))
print(t.hash_of(Test, False))