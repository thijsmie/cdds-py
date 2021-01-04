from cdds.core import Entity, DDSException
from cdds.internal import c_call
from cdds.internal.dds_types import dds_domainid_t, dds_entity_t

from typing import Optional, List
from ctypes import c_char_p, c_size_t, POINTER, byref, cast


class Domain(Entity):
    def __init__(self, domainid: int, config: Optional[str] = None):
        self._id = domainid
        if config is not None:
            super().__init__(self._create_domain(dds_domainid_t(domainid), config.encode("ascii")))
        else:
            super().__init__(self._create_domain(dds_domainid_t(domainid), None))

    def get_participants(self) -> List[Entity]:
        num_participants = self._lookup_participant(self._id, None, 0)
        if num_participants < 0:
            raise DDSException(num_participants, f"Occurred when getting the number of participants of domain {self._id}")
        elif num_participants == 0:
            return []

        participants_list = (dds_entity_t * num_participants)()

        ret = self._lookup_participant(self._id, cast(byref(participants_list), POINTER(dds_entity_t)), num_participants)
        if ret >= 0:
            return [Entity.get_entity(participants_list[i]) for i in range(ret)]

        raise DDSException(ret, f"Occurred when getting the participants of domain {self._id}")

    @c_call("dds_create_domain")
    def _create_domain(self, id: dds_domainid_t, config: c_char_p) -> dds_entity_t:
        pass

    @c_call("dds_lookup_participant")
    def _lookup_participant(self, id: dds_domainid_t, participants: POINTER(dds_entity_t), size: c_size_t) -> dds_entity_t:
        pass
