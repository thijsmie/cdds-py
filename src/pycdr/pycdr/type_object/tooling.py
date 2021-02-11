from typing import get_origin, get_args
from pycdr.types import primitive_types


try:
    from typing import Annotated
except:
    from typing_extensions import Annotated


def is_plain_type(_type):
    if _type in primitive_types:
        return True
    if get_origin(_type) in [dict, list]:
        if True:  # if get_annotations_of(_type) - [External] - [TryConstruct] == []
            return True
    if get_origin(_type) == Annotated:
        _subtype, _annot = get_args(_type)
        if _subtype == list and _annot[0] in ['Len', 'Maxlen']:
            if True:  # if get_annotations_of(_type) - [External] - [TryConstruct] == []
                return True
    return False
