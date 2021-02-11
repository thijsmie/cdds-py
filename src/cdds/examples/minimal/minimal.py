from cdds.domain import DomainParticipant
from cdds.pub import Publisher, DataWriter
from cdds.sub import Subscriber, DataReader
from cdds.core import ReadCondition, SampleState, ViewState, InstanceState, Policy, Qos
from cdds.util import duration

from topic import data, datatopic

"""
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
"""
class Common:
    def __init__(self, domain_id=0):
        self.qos = Qos(Policy.Reliability.Reliable(duration(seconds=2)), Policy.History.KeepLast(10))

        self.dp = DomainParticipant(domain_id)
        self.tp = datatopic(self.dp)
        self.pub = Publisher(self.dp)
        self.sub = Subscriber(self.dp)
        self.dw = DataWriter(self.pub, self.tp, qos=self.qos)
        self.dr = DataReader(self.sub, self.tp, qos=self.qos)
common_setup = Common()

rc = ReadCondition(common_setup.dr, SampleState.Any | ViewState.Any | InstanceState.NotAliveDisposed)

assert not rc.triggered

messages = [data(id=i, name=f"Hi {i}!") for i in range(5)]
for m in messages:
    common_setup.dw.write(m)

received = common_setup.dr.read(N=5)

assert messages == received

common_setup.dw.dispose(messages[1])
assert rc.triggered

received = common_setup.dr.read(condition=rc)

assert len(received) == 1 and received[0] == messages[1]
