from asyncio import run
from aiocdds.async_interfaces import AsyncDataReader

from cdds.core import Qos, Policy
from cdds.util import duration

from vehicle import Vehicle


qos = Qos(
    Policy.Reliability.BestEffort(duration(seconds=1)),
    Policy.Deadline(duration(microseconds=10)),
    Policy.Durability.Transient
)
qos += Policy.History.KeepLast(10)

async def task():
    async for message in AsyncDataReader(topic_name="Vehicle", topic_data=Vehicle, qos=qos):
        print(f"Read sample: Vehicle({message.name}, {message.x}, {message.y})")

run(task())