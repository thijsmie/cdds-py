from cdds.topic import Sample
from ctypes import c_char_p, c_uint16


@Sample("message")
class Message:
    message: c_char_p

@Sample("message")
class MessageAlt:
    user_id: c_uint16
    message: c_char_p
