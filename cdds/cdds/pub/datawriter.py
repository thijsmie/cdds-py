from cdds.core import Entity
from cdds.pub import Publisher
from cdds.topic import Topic
from cdds.internal import c_call, dds_entity_t, dds_qos_p_t, dds_listener_p_t, dds_return_t
from ctypes import c_void_p


class DataWriter(Entity):
    def __init__(self, publisher: Publisher, topic: Topic, qos=None, listener=None):
        self.publisher = publisher
        self.topic = topic
        self.qos = qos
        self.listener = listener
        self._ref = self._create_writer(publisher._ref, topic._ref, qos, listener)

    def write(self, sample):
        # TODO: raise exception based on return code instead, maybe with another decorator
        return self._write(self._ref, sample._ref)

    def dispose_instance(self, sample):
        return self._dispose(self._ref, sample._ref)


    @c_call("dds_create_writer")
    def _create_writer(self, publisher: dds_entity_t, topic: dds_entity_t, qos: dds_qos_p_t, listener: dds_listener_p_t) -> dds_entity_t:
        pass

    @c_call("dds_write")
    def _write(self, writer: dds_entity_t, sample: c_void_p) -> dds_return_t:
        pass

    @c_call("dds_dispose")
    def _dispose(self, writer: dds_entity_t, sample: c_void_p) -> dds_return_t:
        pass