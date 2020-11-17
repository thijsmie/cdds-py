import time

import cdds as dds
from cdds.core.policy import QosDurability, Qos, QosHistory
import vehicle


qos = Qos(durability=QosDurability.Persistent, history=(QosHistory.KeepAll, 200), props={"a": "wow!"})
domain_participant = dds.domain.DomainParticipant(0)
topic = dds.topic.Topic(domain_participant, vehicle.Vehicle, 'Vehicle', qos=None)
subscriber = dds.sub.Subscriber(domain_participant)


reader = dds.sub.DataReader(domain_participant, topic)

while True:
    sample = reader.take()
    if sample:
        sample = sample[0]
        print(f"Received sample: Vehicle({sample.name}, {sample.x}, {sample.y})")
        continue
    time.sleep(1)
