import time

from cdds.domain import DomainParticipant
from cdds.pub import Publisher, DataWriter
from cdds.core import Qos, Policy
from cdds.util.time import duration

from topic import data, datatopic


qos = Qos(Policy.Reliability.Reliable(duration(seconds=2)), Policy.History.KeepLast(10))
dp = DomainParticipant(0)
tp = datatopic(dp)

p = Publisher(dp)
dw = DataWriter(p, tp)

time.sleep(0.5)
print("Calling write")

dw.write(data(id=1, name="hoi"))
dw.write(data(id=2, name="hoi"))
dw.write(data(id=3, name="hoi"))


