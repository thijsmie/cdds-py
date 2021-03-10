"""
 * Copyright(c) 2021 ADLINK Technology Limited and others
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License v. 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0, or the Eclipse Distribution License
 * v. 1.0 which is available at
 * http://www.eclipse.org/org/documents/edl-v10.php.
 *
 * SPDX-License-Identifier: EPL-2.0 OR BSD-3-Clause
"""

from cyclonedds.core import Listener, WaitSet, QueryCondition, ViewState, SampleState, InstanceState, Qos, Policy
from cyclonedds.domain import DomainParticipant
from cyclonedds.topic import Topic
from cyclonedds.sub import Subscriber, DataReader
from cyclonedds.util import duration

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
