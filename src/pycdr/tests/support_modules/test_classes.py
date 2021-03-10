from pycdr import cdr
from pycdr.types import sequence, bound_str, array, uint16

from enum import IntEnum, auto


@cdr
class SingleInt:
    value: int


@cdr
class SingleString:
    value: str


@cdr
class SingleFloat:
    value: float


@cdr
class SingleBool:
    value: bool


@cdr
class SingleSequence:
    value: sequence[int]


@cdr
class SingleArray:
    value: array[uint16, 3]


@cdr
class SingleUint16:
    value: uint16


@cdr
class SingleBoundedSequence:
    value: sequence[int, 3]


@cdr
class SingleBoundedString:
    value: bound_str[10]


class BasicEnum(IntEnum):
    One = auto()
    Two = auto()
    Three = auto()


@cdr
class SingleEnum:
    value: BasicEnum


@cdr
class SingleNested:
    value: SingleInt
