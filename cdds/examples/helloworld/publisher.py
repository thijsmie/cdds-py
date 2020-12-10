import time
import random

from cdds.core import Qos, Policy
from cdds.domain import DomainParticipant
from cdds.pub import Publisher, DataWriter
from cdds.topic import Topic
from cdds.util.time import duration

from vehicle import Vehicle

qos = Qos(
    Policy.Reliability.BestEffort(duration(seconds=1)),
    Policy.Deadline(duration(microseconds=10)),
    Policy.Durability.Transient
)
qos += Policy.History.KeepLast(10)

domain_participant = DomainParticipant(0)
topic = Topic(domain_participant, Vehicle, 'Vehicle', qos=qos)
publisher = Publisher(domain_participant)
writer = DataWriter(publisher, topic)


cart = Vehicle(name=b"Fiat Panda", x=200, y=200)


while True:
    cart.x += random.choice([-1, 0, 1])
    cart.y += random.choice([-1, 0, 1])
    writer.write(cart)
    print(">> Wrote cart")
    time.sleep(random.random() * 0.9 + 0.1)
    
