from cdds.internal import load_library


class DDS:
    """Common class for all DDS related classes. The dll_handle here enables the c_call magic."""
    dll_handle = load_library("ddsc")
    
    # These types will be filled upon import, which makes sure that no circular imports are needed
    entity_type = None
    qos_type = None
    listener_type = None
    
    def __init__(self, ref) -> None:
        self._ref = ref
