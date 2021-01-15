from cdds.internal import load_library


class DDS:
    """Common class for all DDS related classes. This class enables the c_call magic."""
    _dll_handle = load_library("ddsc")

    # These types will be filled upon import, which makes sure that no circular imports are needed
    _entity_type = None
    _qos_type = None
    _listener_type = None

    def __init__(self, reference: int) -> None:
        if self._dll_handle is None:
            raise Exception("The DDSC library could not be located. Check your installation. "
                            "You can manually supply the full path by setting the environment variable 'ddsc'.")
        self._ref = reference
