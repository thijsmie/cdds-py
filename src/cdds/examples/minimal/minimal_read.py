import time

from cdds.domain import DomainParticipant
from cdds.sub import Subscriber, DataReader

from pycdr import cdr, keylist

from topic import data, datatopic


dp = DomainParticipant(0)
tp = datatopic(dp)

s = Subscriber(dp)
dr = DataReader(s, tp)


while True:
    d = dr.take()
    if d:
        print(d)
        break
    time.sleep(0.01)