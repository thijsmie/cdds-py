import time
import random

import cdds as dds
from vehicle import Vehicle

qos = dds.core.policy.Qos(
    durability=dds.core.policy.QosDurability.Transient, 
    history=(dds.core.policy.QosHistory.KeepLast, 20), 
    props={"a": "wow!"}
)

domain_participant = dds.domain.DomainParticipant(0)
topic = dds.topic.Topic(domain_participant, Vehicle, 'Vehicle', qos=qos)
publisher = dds.pub.Publisher(domain_participant)
writer = dds.pub.DataWriter(publisher, topic)


cart = Vehicle(name=b"Fiat Panda", x=200, y=200)


while True:
    cart.x += random.choice([-1, 0, 1])
    cart.y += random.choice([-1, 0, 1])
    writer.write(cart)
    print(">> Wrote cart")
    time.sleep(random.random() * 0.9 + 0.1)
    
