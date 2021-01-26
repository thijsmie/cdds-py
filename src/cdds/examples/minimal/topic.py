from cdds.topic import Topic

from pycdr import cdr, keylist


@keylist('id')
@cdr
class data:
    id: int
    name: str


def datatopic(dp):
    return Topic(dp, "Data", data)