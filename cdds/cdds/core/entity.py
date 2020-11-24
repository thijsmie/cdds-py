from cdds.internal import c_call, DDSException
from cdds.internal.dds_types import dds_instance_handle_t, dds_entity_t, dds_return_t, dds_guid_t, dds_qos_p_t, dds_listener_p_t, dds_domainid_t
from cdds.core import DDS, Qos

from ctypes import POINTER, byref, c_uint32, c_size_t
from typing import Optional, Dict


class Entity(DDS):
    """Maintain a global map of entities to be able to return python objects when the API hands us dds_entity_t references."""
    _entities: Dict[dds_entity_t, 'Entity'] = {}

    def __init__(self, ref) -> None:
        if ref < 0:
            raise DDSException(ref, f"Occurred upon initialisation of a {self.__class__.__module__}.{self.__class__.__name__}.")
        super().__init__(ref)
        self._entities[self._ref] = self

    def __del__(self):
        del self._entities[self._ref]
        self._delete(self._ref)

    def get_subscriber(self):
        ref = self._get_subscriber(self._ref)
        if ref >= 0:
            return self.get_entity(ref)
        raise DDSException(ref, f"Occurred when getting the subscriber for {repr(self)}")

    subscriber = property(get_subscriber, doc="Entity subscriber")

    def get_datareader(self):
        ref = self._get_datareader(self._ref)
        if ref >= 0:
            return self.get_entity(ref)
        raise DDSException(ref, f"Occurred when getting the datareader for {repr(self)}")

    datareader = property(get_datareader, doc="Entity datareader")

    def get_instance_handle(self):
        handle = dds_instance_handle_t()
        ret = self._get_instance_handle(self._ref, byref(handle))
        if ret == 0:
            return int(handle)
        raise DDSException(ret, f"Occurred when getting the instance handle for {repr(self)}")

    instance_handle = property(get_instance_handle, doc="Entity instance handle")

    def get_guid(self):
        guid = dds_guid_t()
        ret = self._get_guid(self._ref, byref(guid))
        if ret == 0:
            return guid.as_python_guid()
        raise DDSException(ret, f"Occurred when getting the GUID for {repr(self)}")

    guid = property(get_guid, doc="Entity GUID")

    def read_status(self, mask=None):
        status = c_uint32()
        ret = self._read_status(self._ref, byref(status), c_uint32(mask) if mask else None)
        if ret == 0:
            return status
        raise DDSException(ret, f"Occurred when reading the status for {repr(self)}")

    def take_status(self):
        status = c_uint32()
        ret = self._take_status(self._ref, byref(status))
        if ret == 0:
            return status
        raise DDSException(ret, f"Occurred when taking the status for {repr(self)}")

    def get_status_changes(self):
        status = c_uint32()
        ret = self._get_status_changes(self._ref, byref(status))
        if ret == 0:
            return status
        raise DDSException(ret, f"Occurred when getting the status changes for {repr(self)}")

    def get_status_mask(self):
        mask = c_uint32()
        ret = self._get_status_mask(self._ref, byref(mask))
        if ret == 0:
            return mask
        raise DDSException(ret, f"Occurred when getting the status mask for {repr(self)}")

    def set_status_mask(self, mask):
        ret = self._set_status_mask(self._ref, c_uint32(mask))
        if ret == 0:
            return
        raise DDSException(ret, f"Occurred when setting the status mask for {repr(self)}")

    status_mask = property(get_status_mask, set_status_mask, doc="Entity status mask")

    def get_qos(self) -> Qos:
        qos = Qos()
        ret = self._get_qos(self._ref, qos._ref)
        if ret == 0:
            return qos
        raise DDSException(ret, f"Occurred when getting the Qos Policies for {repr(self)}")

    def set_qos(self, qos: Qos) -> None:
        ret = self._set_qos(self._ref, qos._ref)
        if ret == 0:
            return
        raise DDSException(ret, f"Occurred when setting the Qos Policies for {repr(self)}")

    qos = property(get_qos, set_qos, doc="Entity QOS")

    def get_listener(self) -> 'Listener':
        listener = self.listener_type()
        ret = self._get_listener(self._ref, listener._ref)
        if ret == 0:
            return listener
        raise DDSException(ret, f"Occurred when getting the Listener for {repr(self)}")

    def set_listener(self, listener: 'Listener') -> None:
        ret = self._set_listener(self._ref, listener._ref)
        if ret == 0:
            return
        raise DDSException(ret, f"Occurred when setting the Listener for {repr(self)}")

    listener = property(get_listener, set_listener, doc="Entity Listener")

    def get_parent(self):
        ret = self._get_parent(self._ref)
        if ret > 0:
            return self.get_entity(ret)
        elif ret is None or ret == 0:
            return None

        raise DDSException(ret, f"Occurred when getting the parent of {repr(self)}")

    parent = property(get_parent, doc="Entity parent")

    def get_participant(self):
        ret = self._get_participant(self._ref)
        if ret > 0:
            return self.get_entity(ret)
        elif ret is None or ret == 0:
            return None

        raise DDSException(ret, f"Occurred when getting the participant of {repr(self)}")

    participant = property(get_participant, doc="Entity Domain Participant")
    domain_participant = property(get_participant, doc="Entity Domain Participant")

    def get_children(self):
        num_children = self._get_children(self._ref, None, 0)
        if num_children < 0:
            raise DDSException(num_children, f"Occurred when getting the number of children of {repr(self)}")
        elif num_children == 0:
            return []
            
        children_list = dds_entity_t * int(num_children)

        ret = self._get_children(self._ref, byref(children_list[0]), num_children)
        if ret >= 0:
            return [self.get_entity(children_list[i]) for i in range(ret)]

        raise DDSException(ret, f"Occurred when getting the children of {repr(self)}")

    children = property(get_children, "Entity Children")

    def get_domainid(self):
        domainid = dds_domainid_t()
        ret = self._get_domainid(self._ref, byref(domainid))
        if ret == 0:
            return int(domainid)

        raise DDSException(ret, f"Occurred when getting the domainid of {repr(self)}")

    domainid = property(get_domainid, "Entity domainid")
       
    @classmethod
    def get_entity(cls, id) -> Optional['Entity']:
        cls._entities.get(id)

    @classmethod
    def _init_from_retcode(cls, code):
        """ This method is called when we are instantiating a code from a dds_entity_t instead of user initialized python. """
        entity = cls.__new__(cls)
        Entity.__init__(entity, code)
        return entity

    @c_call("dds_delete")
    def _delete(self, entity: dds_entity_t) -> None:
        pass

    @c_call("dds_get_subscriber")
    def _get_subscriber(self, entity: dds_entity_t) -> dds_entity_t:
        pass

    @c_call("dds_get_datareader")
    def _get_datareader(self, entity: dds_entity_t) -> dds_entity_t:
        pass

    @c_call("dds_get_instance_handle")
    def _get_instance_handle(self, entity: dds_entity_t, handle: POINTER(dds_instance_handle_t)) -> dds_return_t:
        pass

    @c_call("dds_get_guid")
    def _get_guid(self, entity: dds_entity_t, guid: POINTER(dds_guid_t)) -> dds_return_t:
        pass

    @c_call("dds_read_status")
    def _read_status(self, entity: dds_entity_t, status: POINTER(c_uint32), mask: c_uint32) -> dds_return_t:
        pass

    @c_call("dds_take_status")
    def _take_status(self, entity: dds_entity_t, status: POINTER(c_uint32)) -> dds_return_t:
        pass

    @c_call("dds_get_status_changes")
    def _get_status_changes(self, entity: dds_entity_t, status: POINTER(c_uint32)) -> dds_return_t:
        pass

    @c_call("dds_get_status_mask")
    def _get_status_mask(self, entity: dds_entity_t, mask: POINTER(c_uint32)) -> dds_return_t:
        pass

    @c_call("dds_get_qos")
    def _get_qos(self, entity: dds_entity_t, qos: dds_qos_p_t) -> dds_return_t:
        pass

    @c_call("dds_set_qos")
    def _set_qos(self, entity: dds_entity_t, qos: dds_qos_p_t) -> dds_return_t:
        pass

    @c_call("dds_get_listener")
    def _get_listener(self, entity: dds_entity_t, listener: dds_listener_p_t) -> dds_return_t:
        pass

    @c_call("dds_set_listener")
    def _set_listener(self, entity: dds_entity_t, listener: dds_listener_p_t) -> dds_return_t:
        pass

    @c_call("dds_get_parent")
    def _get_parent(self, entity: dds_entity_t) -> dds_entity_t:
        pass

    @c_call("dds_get_participant")
    def _get_participant(self, entity: dds_entity_t) -> dds_entity_t:
        pass

    @c_call("dds_get_children")
    def _get_children(self, entity: dds_entity_t, children_list: POINTER(dds_return_t), size: c_size_t) -> dds_return_t:
        pass

    @c_call("dds_get_domainid")
    def _get_domainid(self, entity: dds_entity_t, domainid: POINTER(dds_domainid_t)) -> dds_return_t:
        pass

    def __repr__(self) -> str:
        return f"<Entity, type={self.__class__.__module__}.{self.__class__.__name__}, addr={hex(id(self))}, id={self._ref}>"


DDS.entity_type = Entity