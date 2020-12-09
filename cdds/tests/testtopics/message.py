from cdds.domain import Sample
from ctypes import c_char_p


@Sample("message")
class Message:
    message: c_char_p
