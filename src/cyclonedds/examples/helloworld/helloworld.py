from cyclonedds.domain import DomainParticipant
from cyclonedds.pub import Publisher, DataWriter
from cyclonedds.sub import Subscriber, DataReader
from cyclonedds.topic import Topic

from pycdr import cdr


@cdr
class HelloWorld:
    data: str


dp = DomainParticipant()
tp = Topic(dp, "Hello", HelloWorld)

pub = Publisher(dp)
dw = DataWriter(pub, tp)

sub = Subscriber(dp)
dr = DataReader(sub, tp)


dw.write(HelloWorld(data='Hello, World!'))
print(dr.read()[0].data)