from typing import Optional, Union

from .core import Entity, DDSException
from .internal import c_call, dds_c_t
from ddspy import ddspy_read, ddspy_take


class Subscriber(Entity):
    def __init__(self, 
        domain_participant: 'cyclonedds.domain.DomainParticipant', 
        qos: Optional['cyclonedds.core.Qos']=None, 
        listener: Optional['cyclonedds.core.Listener']=None
    ):
        super().__init__(
            self._create_subscriber(
                domain_participant._ref,
                qos._ref if qos else None,
                listener._ref if listener else None
            )
        )

    @c_call("dds_create_subscriber")
    def _create_subscriber(self, domain_participant: dds_c_t.entity, qos: dds_c_t.qos_p,
                           listener: dds_c_t.listener_p) -> dds_c_t.entity:
        pass


class DataReader(Entity):
    """
    """

    def __init__(self, 
        subscriber_or_participant: Union['cyclonedds.sub.Subscriber', 'cyclonedds.domain.DomainParticipant'],
        topic: 'cyclonedds.topic.Topic', 
        qos: Optional['cyclonedds.core.Qos']=None, 
        listener: Optional['cyclonedds.core.Listener']=None
    ):
        super().__init__(
            self._create_reader(
                subscriber_or_participant._ref,
                topic._ref,
                qos._ref if qos else None,
                listener._ref if listener else None
            )
        )

    def read(self, N=1, condition=None):
        ret = ddspy_read(condition._ref if condition else self._ref, N)
        if type(ret) == int:
            raise DDSException(ret, f"Occurred while reading data in {repr(self)}")
        return ret

    def take(self, N=1, condition=None):
        ret = ddspy_take(condition._ref if condition else self._ref, N)
        if type(ret) == int:
            raise DDSException(ret, f"Occurred while taking data in {repr(self)}")
        return ret

    def wait_for_historical_data(self, timeout: int) -> bool:
        ret = self._wait_for_historical_data(self._ref, timeout)

        if ret == 0:
            return True
        elif ret == DDSException.DDS_RETCODE_TIMEOUT:
            return False
        raise DDSException(ret, f"Occured while waiting for historical data in {repr(self)}")

    @c_call("dds_create_reader")
    def _create_reader(self, subscriber: dds_c_t.entity, topic: dds_c_t.entity, qos: dds_c_t.qos_p,
                       listener: dds_c_t.listener_p) -> dds_c_t.entity:
        pass

    @c_call("dds_reader_wait_for_historical_data")
    def _wait_for_historical_data(self, reader: dds_c_t.entity, max_wait: dds_c_t.duration) -> dds_c_t.returnv:
        pass
