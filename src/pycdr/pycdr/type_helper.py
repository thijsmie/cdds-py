import sys


if sys.version_info < (3, 6):
    raise NotImplementedError("This package cannot be used in Python version 3.5 or lower.")
elif sys.version_info < (3, 7):
    # We are in any Python 3.6 version
    from typing_extensions import Annotated
    from typing_inspect import get_origin, get_args
elif sys.version_info < (3, 9):
    # We are in any Python 3.7 or 3.8 version
    from typing_extensions import Annotated, get_origin, get_args
else:
    # We are in any Python 3.9 or 3.10 (maybe higher?) version
    from typing import Annotated, get_origin, get_args
