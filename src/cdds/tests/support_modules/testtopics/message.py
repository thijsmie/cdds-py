from pycdr import cdr


@cdr
class Message:
    message: str


@cdr
class MessageAlt:
    user_id: int
    message: str
