import pytest

from cdds.core import Qos, Policy
from cdds.domain import DomainParticipant
from cdds.topic import Topic
from cdds.pub import Publisher, DataWriter
from cdds.sub import Subscriber, DataReader
from cdds.util.time import duration

# Allow the import of support modules for tests
import os.path as p
import sys
sys.path.append(p.join(p.abspath(p.dirname(__file__)), "support_modules/"))

from testtopics import Message

class Common:
    def __init__(self, domain_id=0):
        self.qos = Qos(Policy.Reliability.Reliable(duration(seconds=2)), Policy.History.KeepLast(10))

        self.dp = DomainParticipant(domain_id)
        self.tp = Topic(self.dp, 'Message', Message)
        self.pub = Publisher(self.dp)
        self.sub = Subscriber(self.dp)
        self.dw = DataWriter(self.pub, self.tp, qos=self.qos)
        self.dr = DataReader(self.sub, self.tp, qos=self.qos)

global domain_id_counter
domain_id_counter = 0

@pytest.fixture
def common_setup():
    # Ensuring a unique domain id for each setup ensures parellization options
    global domain_id_counter
    domain_id_counter += 1
    return Common(domain_id=domain_id_counter)