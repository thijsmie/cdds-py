from cdds.core import WaitSet, ReadCondition, ViewState, InstanceState, SampleState
from cdds.domain import DomainParticipant
from cdds.sub import Subscriber, DataReader
from cdds.util.time import duration
from cdds.topic import Topic

from asyncio import get_event_loop, ensure_future, QueueEmpty
from janus import Queue

global default_participant
default_participant = None
in_loop_participants = {}


def MakeDefaultParticipant():
    global default_participant
    if default_participant is None:
        default_participant = DomainParticipant()


def ThreadParticipant(participant, condition_queue):
    waitset = WaitSet(participant)
    connections = {}

    while True:
        # Add new conditions
        while not condition_queue.empty():
            try:
                (condition, reader, data_queue) = condition_queue.get_nowait()
                waitset.attach(condition)
                connections[condition] = (data_queue, reader)
            except QueueEmpty:
                break
        
        if waitset.wait(duration(milliseconds=10)):
            for condition, (data_queue, reader) in connections.items():
                if condition.triggered():
                    for sample in reader.read(condition=condition, N=100):
                        data_queue.put(sample)

                


async def EnsureMyLoop(domain_participant, reader, condition):
    loop = get_event_loop()
    data_queue = Queue().sync_q

    if not domain_participant._ref in in_loop_participants:
        condition_queue = Queue().sync_q
        condition_queue.put((condition, reader, data_queue))

        ensure_future(loop.run_in_executor(None, ThreadParticipant, domain_participant, condition_queue))

        in_loop_participants[domain_participant._ref] = condition_queue
    else:
        in_loop_participants[domain_participant._ref].put((condition, reader, data_queue))
    
    return data_queue


class AsyncDataReader:
    def __init__(self, *, qos=None, topic_data, topic_name, domain_participant=None, condition=None) -> None:
        global default_participant
        if domain_participant is None:
            if default_participant is None:
                MakeDefaultParticipant()
            self.domain_participant = default_participant
        else:
            self.domain_participant = domain_participant

        self.data_queue = None
        self.subscriber = Subscriber(self.domain_participant, qos)
        self.topic = Topic(self.domain_participant, topic_data, topic_name, qos)
        self.datareader = DataReader(self.subscriber, self.topic, qos)
        self.condition = condition or ReadCondition(self.datareader, ViewState.Any | SampleState.NotRead | InstanceState.Alive)

    async def _setup(self):
        self.data_queue = await EnsureMyLoop(self.domain_participant, self.datareader, self.condition)

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self.data_queue:
            await self._setup()
        return self.data_queue.get()

class AsyncDataWriter:
    pass

class AsyncDataPipe:
    pass