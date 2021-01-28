import cdds
from cdds.internal import DDS, c_call
from cdds.internal.dds_types import dds_instance_handle_t, dds_entity_t, dds_return_t, dds_guid_t, \
                                    dds_qos_p_t, dds_listener_p_t, dds_domainid_t
from cdds.core import Qos, DDSException

from ctypes import POINTER, byref, c_uint32, c_size_t, cast
from typing import List, Optional, Dict
from weakref import WeakValueDictionary

from uuid import UUID


class Entity(DDS):
    """
    Base class for all entities in the DDS API. The lifetime of the underlying DDS API object is linked to the lifetime of the Python entity object.

    Attributes
    ----------
    subscriber:  Subscriber, optional
                 If this entity is associated with a DataReader retrieve it. It is read-only. This is a proxy for get_subscriber().
    publisher:   Publisher, optional
                 If this entity is associated with a Publisher retrieve it. It is read-only. This is a proxy for get_publisher().
    datareader:  DataReader, optional
                 If this entity is associated with a DataReader retrieve it. It is read-only. This is a proxy for get_datareader().
    guid:        uuid.UUID
                 Return the globally unique identifier for this entity. It is read-only. This is a proxy for get_guid().
    status_mask: int
                 The status mask for this entity. It is a set of bits formed from ``DDSStatus``. This is a proxy for get/set_status_mask().
    qos:         Qos
                 The quality of service policies for this entity. This is a proxy for get/set_qos().
    listener:    Listener
                 The listener associated with this entity. This is a proxy for get/set_listener().
    parent:      Entity, optional
                 The entity that is this entities parent. For example: the subscriber for a datareader, the participant for a topic.
                 It is read-only. This is a proxy for get_parent().
    participant: DomainParticipant, optional
                 Get the participant for any entity, will only fail for a ``Domain``. It is read-only. This is a proxy for get_participant().
    children:    List[Entity]
                 Get a list of children belonging to this entity. It is the opposite as ``parent``. It is read-only. This is a proxy for get_children().
    domainid:    int
                 Get the id of the domain this entity belongs to.
    """

    _entities: Dict[dds_entity_t, 'Entity'] = WeakValueDictionary()

    def __init__(self, ref: int) -> None:
        """Initialize an Entity. You should never need to initialize an Entity manually.

        Parameters
        ----------
        ref: int
            The reference id as returned by the DDS API.

        Raises
        ------
        DDSException
            If an invalid reference id is passed to this function this means instantiation of some other object failed.
        """
        if ref < 0:
            raise DDSException(ref, f"Occurred upon initialisation of a {self.__class__.__module__}.{self.__class__.__name__}")
        super().__init__(ref)
        self._entities[self._ref] = self

    def __del__(self):
        if not hasattr(self, "_ref") or self._ref not in self._entities:
            return

        del self._entities[self._ref]
        self._delete(self._ref)

    def get_subscriber(self) -> Optional['cdds.sub.subscriber.Subscriber']:
        """Retrieve the subscriber associated with this entity.

        Returns
        -------
        Subscriber, optional
            Not all entities are associated with a subscriber, so this method may return None.

        Raises
        ------
        DDSException
        """
        ref = self._get_subscriber(self._ref)
        if ref >= 0:
            return self.get_entity(ref)
        raise DDSException(ref, f"Occurred when getting the subscriber for {repr(self)}")

    subscriber: 'cdds.sub.subscriber.Subscriber' = property(get_subscriber, doc=None)

    def get_publisher(self) -> Optional['cdds.pub.Publisher']:
        """Retrieve the publisher associated with this entity.

        Returns
        -------
        Publisher, optional
            Not all entities are associated with a publisher, so this method may return None.

        Raises
        ------
        DDSException
        """
        ref = self._get_publisher(self._ref)
        if ref >= 0:
            return self.get_entity(ref)
        raise DDSException(ref, f"Occurred when getting the publisher for {repr(self)}")

    publisher: 'cdds.sub.Publisher' = property(get_publisher)

    def get_datareader(self) -> Optional['cdds.sub.DataReader']:
        """Retrieve the datareader associated with this entity.

        Returns
        -------
        DataReader, optional
            Not all entities are associated with a datareader, so this method may return None.

        Raises
        ------
        DDSException
        """
        ref = self._get_datareader(self._ref)
        if ref >= 0:
            return self.get_entity(ref)
        raise DDSException(ref, f"Occurred when getting the datareader for {repr(self)}")

    datareader: Optional['cdds.sub.DataReader'] = property(get_datareader)

    def get_instance_handle(self) -> int:
        """Retrieve the instance associated with this entity.

        Returns
        -------
        int
            TODO: replace this with some mechanism for an Instance class

        Raises
        ------
        DDSException
        """
        handle = dds_instance_handle_t()
        ret = self._get_instance_handle(self._ref, byref(handle))
        if ret == 0:
            return int(handle)
        raise DDSException(ret, f"Occurred when getting the instance handle for {repr(self)}")

    instance_handle: int = property(get_instance_handle)

    def get_guid(self) -> UUID:
        """Get a globally unique identifier for this entity.

        Returns
        -------
        uuid.UUID
            View the python documentation for this class for detailed usage.

        Raises
        ------
        DDSException
        """
        guid = dds_guid_t()
        ret = self._get_guid(self._ref, byref(guid))
        if ret == 0:
            return guid.as_python_guid()
        raise DDSException(ret, f"Occurred when getting the GUID for {repr(self)}")

    guid: 'UUID' = property(get_guid)

    def read_status(self, mask: int = None) -> int:
        """Read the status bits set on this Entity. You can build a mask by using ``cdds.core.DDSStatus``.

        Parameters
        ----------
        mask : int, optional
            The ``DDSStatus`` mask. If not supplied the mask is used that was set on this Entity using set_status_mask.

        Returns
        -------
        int
            The `DDSStatus`` bits that were set.

        Raises
        ------
        DDSException
        """
        status = c_uint32()
        ret = self._read_status(self._ref, byref(status), c_uint32(mask) if mask else self.get_status_mask())
        if ret == 0:
            return status.value
        raise DDSException(ret, f"Occurred when reading the status for {repr(self)}")

    def take_status(self, mask=None) -> int:
        """Take the status bits set on this Entity, after which they will be set to 0 again.
        You can build a mask by using ``cdds.core.DDSStatus``.

        Parameters
        ----------
        mask : int, optional
            The ``DDSStatus`` mask. If not supplied the mask is used that was set on this Entity using set_status_mask.

        Returns
        -------
        int
            The `DDSStatus`` bits that were set.

        Raises
        ------
        DDSException
        """
        status = c_uint32()
        ret = self._take_status(self._ref, byref(status), c_uint32(mask) if mask else self.get_status_mask())
        if ret == 0:
            return status.value
        raise DDSException(ret, f"Occurred when taking the status for {repr(self)}")

    def get_status_changes(self) -> int:
        """Get all status changes since the last read_status() or take_status().

        Returns
        -------
        int
            The `DDSStatus`` bits that were set.

        Raises
        ------
        DDSException
        """
        status = c_uint32()
        ret = self._get_status_changes(self._ref, byref(status))
        if ret == 0:
            return status.value
        raise DDSException(ret, f"Occurred when getting the status changes for {repr(self)}")

    def get_status_mask(self) -> int:
        """Get the status mask for this Entity.

        Returns
        -------
        int
            The `DDSStatus`` bits that are enabled.

        Raises
        ------
        DDSException
        """
        mask = c_uint32()
        ret = self._get_status_mask(self._ref, byref(mask))
        if ret == 0:
            return mask.value
        raise DDSException(ret, f"Occurred when getting the status mask for {repr(self)}")

    def set_status_mask(self, mask: int) -> None:
        """Set the status mask for this Entity. By default the mask is 0. Only the status changes for the bits in this mask are tracked on this entity.

        Parameters
        ----------
        mask : int
            The ``DDSStatus`` bits to track.

        Raises
        ------
        DDSException
        """
        ret = self._set_status_mask(self._ref, c_uint32(mask))
        if ret == 0:
            return
        raise DDSException(ret, f"Occurred when setting the status mask for {repr(self)}")

    status_mask = property(get_status_mask, set_status_mask)

    def get_qos(self) -> Qos:
        """Get the set of ``Qos`` policies associated with this entity. Note that the object returned is not
        the same python object that you used to set the ``Qos`` on this object. Modifications to the ``Qos`` object
        that is returned does _not_ modify the Qos of the Entity.

        Returns
        -------
        Qos
            The Qos policies associated with this entity.

        Raises
        ------
        DDSException
        """
        qos = Qos()
        ret = self._get_qos(self._ref, qos._ref)
        if ret == 0:
            return qos
        raise DDSException(ret, f"Occurred when getting the Qos Policies for {repr(self)}")

    def set_qos(self, qos: Qos) -> None:
        """Set ``Qos`` policies on this entity. Note, only a limited number of ``Qos`` policies can be set after
        the object is created (``Policy.LatencyBudget`` and ``Policy.OwnershipStrength``). Any policies not set
        explicitly in the supplied ``Qos`` remain.

        Parameters
        ----------
        qos : Qos
            The ``Qos`` to apply to this entity.

        Raises
        ------
        DDSException
            If you pass an immutable policy or cause the total collection of qos policies to become inconsistent
            an exception will be raised.
        """
        ret = self._set_qos(self._ref, qos._ref)
        if ret == 0:
            return
        raise DDSException(ret, f"Occurred when setting the Qos Policies for {repr(self)}")

    qos = property(get_qos, set_qos)

    def get_listener(self) -> 'cdds.core.Listener':
        """Return a listener associated with this object. Modifying the returned listener object does not modify
        this entity, you will have to call set_listener() with the changed object.

        Returns
        -------
        Listener
            A listener with which you can add additional callbacks.

        Raises
        ------
        DDSException
        """
        listener = self.listener_type()
        ret = self._get_listener(self._ref, listener._ref)
        if ret == 0:
            return listener
        raise DDSException(ret, f"Occurred when getting the Listener for {repr(self)}")

    def set_listener(self, listener: 'cdds.core.Listener') -> None:
        """Set the listener for this object. If a listener already exist for this object only the fields you explicitly
        have set on your new listener are overwritten.

        Parameters
        ----------
        listener : Listener
            The listener object to use.

        Raises
        ------
        DDSException
        """
        ret = self._set_listener(self._ref, listener._ref)
        if ret == 0:
            return
        raise DDSException(ret, f"Occurred when setting the Listener for {repr(self)}")

    listener = property(get_listener, set_listener)

    def get_parent(self) -> Optional['Entity']:
        """Get the parent entity associated with this entity. A ``Domain`` object is the only object without parent, but if the domain is
        not created through the Python API this call won't find it and return None from the DomainParticipant.

        Returns
        -------
        Entity, optional
            The parent of this entity. This would be the Subscriber for a DataReader, DomainParticipant for a Topic etc.

        Raises
        ------
        DDSException
        """
        ret = self._get_parent(self._ref)
        if ret > 0:
            return self.get_entity(ret)
        elif ret is None or ret == 0:
            return None

        raise DDSException(ret, f"Occurred when getting the parent of {repr(self)}")

    parent = property(get_parent)

    def get_participant(self) -> Optional['cdds.domain.DomainParticipant']:
        """Get the domain participant for this entity. This should work on all valid Entity objects except a Domain.

        Returns
        -------
        DomainParticipant, optional
            Only fails for a Domain object.

        Raises
        ------
        DDSException
        """
        ret = self._get_participant(self._ref)
        if ret > 0:
            return self.get_entity(ret)
        elif ret is None or ret == 0:
            return None

        raise DDSException(ret, f"Occurred when getting the participant of {repr(self)}")

    participant = property(get_participant)

    def get_children(self) -> List['Entity']:
        """Get the list of children of this entity. For example, the list of datareaders belonging to a subscriber. Opposite of parent.

        Returns
        -------
        List[Entity]
            All the entities considered children of this entity.

        Raises
        ------
        DDSException
        """
        num_children = self._get_children(self._ref, None, 0)
        if num_children < 0:
            raise DDSException(num_children, f"Occurred when getting the number of children of {repr(self)}")
        elif num_children == 0:
            return []

        children_list = (dds_entity_t * int(num_children))()
        children_list_pt = cast(children_list, POINTER(dds_entity_t))

        ret = self._get_children(self._ref, children_list_pt, num_children)
        if ret >= 0:
            return [self.get_entity(children_list[i]) for i in range(ret)]

        raise DDSException(ret, f"Occurred when getting the children of {repr(self)}")

    children = property(get_children)

    def get_domainid(self) -> int:
        """Get the id of the domain this entity resides in.

        Returns
        -------
        int
            The domain id.

        Raises
        ------
        DDSException
        """
        domainid = dds_domainid_t()
        ret = self._get_domainid(self._ref, byref(domainid))
        if ret == 0:
            return domainid.value

        raise DDSException(ret, f"Occurred when getting the domainid of {repr(self)}")

    domainid = property(get_domainid)

    @classmethod
    def get_entity(cls, id) -> Optional['Entity']:
        return cls._entities.get(id)

    @classmethod
    def _init_from_retcode(cls, code):
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

    @c_call("dds_get_publisher")
    def _get_publisher(self, entity: dds_entity_t) -> dds_entity_t:
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
    def _take_status(self, entity: dds_entity_t, status: POINTER(c_uint32), mask: c_uint32) -> dds_return_t:
        pass

    @c_call("dds_get_status_changes")
    def _get_status_changes(self, entity: dds_entity_t, status: POINTER(c_uint32)) -> dds_return_t:
        pass

    @c_call("dds_get_status_mask")
    def _get_status_mask(self, entity: dds_entity_t, mask: POINTER(c_uint32)) -> dds_return_t:
        pass

    @c_call("dds_set_status_mask")
    def _set_status_mask(self, entity: dds_entity_t, mask: c_uint32) -> dds_return_t:
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
        ref = None
        try:
            ref = self._ref
        except Exception:
            pass
        return f"<Entity, type={self.__class__.__module__}.{self.__class__.__name__}, addr={hex(id(self))}, id={ref}>"


DDS.entity_type = Entity
