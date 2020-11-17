import time

import cdds as dds
import vehicle


domain_participant = dds.domain.DomainParticipant(0)
topic = dds.topic.Topic(domain_participant, vehicle.Vehicle, 'Vehicle')
publisher = dds.pub.Publisher(domain_participant)
writer = dds.pub.DataWriter(publisher, topic)


cart = vehicle.Vehicle(name=b"Bazinga", x=20, y=20)


while True:
    writer.write(cart)
    cart.x += 1
    cart.y += 1
    print(">> wrote cart")
    time.sleep(1)
    
