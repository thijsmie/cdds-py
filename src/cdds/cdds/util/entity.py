from cdds.core import Entity


def isgoodentity(v: object) -> bool:
    """Helper function that checks to see if an object is a valid :class:`Entity<cdds.core.entity.Entity>` returned from DDS.
    This function will never raise an exception.

    Parameters
    ----------
    v : object, optional
        The object to check

    Returns
    -------
    bool
        Whether this entity is a valid :class:`Entity<cdds.core.entity.Entity>`.
    """
    return v is not None and \
           isinstance(v, Entity) and \
           hasattr(v, "_ref") and \
           type(v._ref) == int and \
           v._ref > 0
