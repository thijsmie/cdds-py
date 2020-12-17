import cdds
from cdds.core import Entity, DDSException
from cdds.internal import c_call, dds_entity_t, dds_return_t
from ctypes import POINTER, c_bool, byref


class GuardCondition(Entity):
    """ A GuardCondition is a manually triggered condition that can be added to a :class:`WaitSet<cdds.core.waitset.WaitSet>`."""

    def __init__(self, domain_participant: 'DomainParticipant'):
        """Initialize a GuardCondition
        
        Parameters
        ----------
        domain_participant: DomainParticipant
            The domain in which the GuardCondition should be active.
        """

        super().__init__(self._create_guardcondition(domain_participant._ref))

    def set(self, triggered: bool) -> None:
        """Set the status of the GuardCondition to triggered or untriggered.

        Parameters
        ----------
        triggered: bool
            Wether to trigger this condition.

        Returns
        -------
        None

        Raises
        ------
        DDSException
        """
        ret = self._set_guardcondition(self._ref, triggered)
        if ret < 0:
            raise DDSException(ret, f"Occurred when calling set on {repr(self)}")

    def read(self) -> bool:
        """Read the status of the GuardCondition.

        Returns
        ----------
        bool
            Wether this condition is triggered.

        Raises
        ------
        DDSException
        """
        triggered = c_bool()
        ret = self._read_guardcondition(self._ref, byref(triggered))
        if ret < 0:
            raise DDSException(ret, f"Occurred when calling read on {repr(self)}")
        return bool(triggered)

    def take(self) -> bool:
        """Take the status of the GuardCondition. If it is True it will be False on the next call.

        Returns
        ----------
        bool
            Wether this condition is triggered.

        Raises
        ------
        DDSException
        """
        triggered = c_bool()
        ret = self._take_guardcondition(self._ref, byref(triggered))
        if ret < 0:
            raise DDSException(ret, f"Occurred when calling read on {repr(self)}")
        return bool(triggered)

    @c_call("dds_create_guardcondition")
    def _create_guardcondition(self, participant: dds_entity_t) -> dds_entity_t:
        pass

    @c_call("dds_set_guardcondition")
    def _set_guardcondition(self, guardcond: dds_entity_t, triggered: c_bool) -> dds_return_t:
        pass

    @c_call("dds_read_guardcondition")
    def _read_guardcondition(self, guardcond: dds_entity_t, triggered: POINTER(c_bool)) -> dds_return_t:
        pass

    @c_call("dds_take_guardcondition")
    def _take_guardcondition(self, guardcond: dds_entity_t, triggered: POINTER(c_bool)) -> dds_return_t:
        pass
