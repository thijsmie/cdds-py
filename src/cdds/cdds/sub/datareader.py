import cdds

from cdds.core import Entity, DDSException
from cdds.internal import c_call
from cdds.internal.dds_types import dds_entity_t, dds_qos_p_t, dds_listener_p_t, dds_return_t, dds_duration_t
from cdds.core.exception import DDS_RETCODE_TIMEOUT

from typing import Union

from ddspy import ddspy_read, ddspy_take


class DataReader(Entity):
    """
    """

    def __init__(self, subscriber_or_participant: Union['cdds.sub.Subscriber', 'cdds.domain.DomainParticipant'],
                 topic: 'cdds.topic.Topic', qos=None, listener=None):
        self.topic = topic
        self._N = 0
        self._sampleinfos = None
        self._pt_sampleinfos = None
        self._samples = None
        self._pt_samples = None
        self._pt_void_samples = None
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
        elif ret == DDS_RETCODE_TIMEOUT:
            return False
        raise DDSException(ret, f"Occured while waiting for historical data in {repr(self)}")

    @c_call("dds_create_reader")
    def _create_reader(self, subscriber: dds_entity_t, topic: dds_entity_t, qos: dds_qos_p_t,
                       listener: dds_listener_p_t) -> dds_entity_t:
        pass

    @c_call("dds_reader_wait_for_historical_data")
    def _wait_for_historical_data(self, reader: dds_entity_t, max_wait: dds_duration_t) -> dds_return_t:
        pass
