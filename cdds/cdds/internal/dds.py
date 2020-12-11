from cdds.internal import load_library


class DDS:
    """Common class for all DDS related classes. This class enables the c_call magic."""
    _dll_handle = load_library("ddsc")

    # These types will be filled upon import, which makes sure that no circular imports are needed
    _entity_type = None
    _qos_type = None
    _listener_type = None

    def __init__(self, reference: int) -> None:
        self._ref = reference
