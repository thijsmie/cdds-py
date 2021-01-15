from typing import NewType, get_type_hints, Any
from dataclasses import dataclass, fields


char = NewType("char", int)
wchar = NewType("wchar", int)
int8 = NewType("int8", int)
int16 = NewType("int16", int)
int32 = NewType("int32", int)
int64 = NewType("int64", int)
uint8 = NewType("uint8", int)
uint16 = NewType("uint16", int)
uint32 = NewType("uint32", int)
uint64 = NewType("uint64", int)
float32 = NewType("float32", float)
float64 = NewType("float64", float)


def MaxLen(a):
    return 'MaxLen', a


def Len(a):
    return 'Len', a


def case(v):
    return 'case', v

def default():
    return ('default',)


class IdlUnion:
    def __init__(self):
        self.discriminator = None
        self.value = None

    def __setattr__(self, name: str, value: Any) -> None:
        if name in self._cases:
            case = self._cases[name]
            self.discriminator = case[0]
            self.value = value
            return
        if self._default and self._default[0] == name:
            self.discriminator = None
            self.value = value
            return
        return super().__setattr__(name, value)

    def __getattr__(self, name: str) -> Any:
        if name in self._cases:
            case = self._cases[name]
            if self.discriminator != case[0]:
                raise AttributeError("Tried to get inactive case on union")
            return self.value
        if self._default and self._default[0] == name:
            if self.discriminator is not None:
                raise AttributeError("Tried to get inactive case on union")
            return self.value
        return super().__getattribute__(name)


def union(discriminator):
    def wraps(cls):
        type_info = get_type_hints(cls, include_extras=True)

        cases = {}
        default = None

        for field, _type in type_info.items():
            case = getattr(cls, field)
            if type(case) != tuple or len(case) < 1:
                raise Exception("Fields of a union need to be case or default.")
            if case[0] == 'default':
                if default is not None:
                    raise Exception("Only one default case is allowed per union.")
                default = (field, _type)
            elif case[0] == 'case':
                cases[field] = (case[1], _type)
            else:
                raise Exception("Fields of a union need to be case or default.")

        class MyUnion(IdlUnion):
            _discriminator = discriminator
            _original_cls = cls
            _cases = cases
            _default = default

        return MyUnion
    return wraps