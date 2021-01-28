from cdds.domain import DomainParticipant
from cdds.pub import Publisher, DataWriter
from cdds.sub import Subscriber, DataReader

from topic import data, datatopic


dp = DomainParticipant(0)
tp = datatopic(dp)

p = Publisher(dp)
s = Subscriber(dp)
dw = DataWriter(p, tp)
dr = DataReader(s, tp)

print("Calling write")
dw.write(data(id=1, name="tsja"))

print("Calling take")
print(dr.take())
print(dr.take())
