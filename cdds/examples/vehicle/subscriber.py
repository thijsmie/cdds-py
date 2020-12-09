import time
import string
import random
from datetime import timedelta

from cdds.core import Listener, WaitSet, ReadCondition, QueryCondition, ViewState, SampleState, InstanceState, Qos, Policy
from cdds.domain import DomainParticipant
from cdds.topic import Topic
from cdds.sub import Subscriber, DataReader
from cdds.util import duration

from vehicle import Vehicle



class MyListener(Listener):
    def on_data_available(self, reader):
        print(">> Ping!")

    def on_liveliness_changed(self, reader, status):
        print(">> Liveliness event")


listener = MyListener()
qos = Qos(
    Policy.Reliability.BestEffort(duration(seconds=1)),
    Policy.Deadline(duration(microseconds=10)),
    Policy.Durability.Transient
)
qos += Policy.History.KeepLast(10)

domain_participant = DomainParticipant(0)
topic = Topic(domain_participant, Vehicle, 'Vehicle', qos=qos)
subscriber = Subscriber(domain_participant)
reader = DataReader(domain_participant, topic, listener=listener)

condition = QueryCondition(reader, SampleState.NotRead | ViewState.Any | InstanceState.Alive, lambda vehicle: vehicle.x % 2 == 0)

waitset = WaitSet(domain_participant)
waitset.attach(condition)

while True:
    waitset.wait(duration(seconds=2.2))
    samples = reader.take(N=100)
    if samples:
        for sample in samples:
            print(f"Read sample: Vehicle({sample.name}, {sample.x}, {sample.y})")
    else:
        print("timeout waitset")