import time

from cdds.domain import DomainParticipant
from cdds.pub import Publisher, DataWriter

from pycdr import cdr, keylist

from topic import data, datatopic


dp = DomainParticipant(0)
tp = datatopic(dp)

p = Publisher(dp)
dw = DataWriter(p, tp)

print("Calling write")
dw.write(data(id=1, name="hoi"))
time.sleep(10)
