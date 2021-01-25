from cdds.domain import DomainParticipant
from cdds.topic import Topic
from cdds.pub import Publisher, DataWriter

from pycdr import cdr, keylist


@keylist('id')
@cdr
class data:
    id: int
    name: str

print("name:", data.typename)
print("keyless:", data.keyless)

dp = DomainParticipant(0)
tp = Topic(dp, "Data", data)

p = Publisher(dp)
dw = DataWriter(p, tp)

print("Calling write")
dw.write(data(id=1, name="tsja"))