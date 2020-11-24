from cdds.core import Entity
from cdds.internal import c_call, DDSException
from cdds.internal.dds_types import dds_domainid_t, dds_entity_t

from ctypes import c_char_p, c_size_t, POINTER, byref


class Domain(Entity):
    def __init__(self, id: int, config: str):
        self.domainid = id
        super().__init__(self._create_domain(id, config.encode("ASCII")))

    def get_participants(self):
        return self.lookup_participants(self.domainid)

    @classmethod
    def lookup_participants(cls, domainid):
        num_participants = cls._lookup_participant(domainid, None, 0)
        if num_participants < 0:
            raise DDSException(num_participants, f"Occurred when getting the number of participants of domain {domainid}")
        elif num_participants == 0:
            return []
            
        participants_list = dds_entity_t * int(num_participants)

        ret = cls._lookup_participant(domainid, byref(participants_list[0]), num_participants)
        if ret >= 0:
            return [cls.get_entity(participants_list[i]) for i in range(ret)]

        raise DDSException(ret, f"Occurred when getting the participants of domain {domainid}")

    @c_call("dds_create_domain")
    def _create_domain(self, id: dds_domainid_t, config: c_char_p) -> dds_entity_t:
        pass

    @c_call("dds_lookup_participant")
    def _lookup_participant(self, id: dds_domainid_t, participants: POINTER(dds_entity_t), size: c_size_t):
        pass

    