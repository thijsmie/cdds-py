from cdds.topic import Topic
from cdds.core import Qos, Policy
from cdds.util.time import duration

from pycdr import cdr, keylist


@keylist('id')
@cdr
class data:
    id: int
    name: str


qos = Qos(Policy.Reliability.Reliable(duration(seconds=2)), Policy.History.KeepLast(10))
def datatopic(dp):
    return Topic(dp, "Data", data, qos=qos)