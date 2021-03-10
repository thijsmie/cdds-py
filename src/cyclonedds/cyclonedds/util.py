try:
    from time import time_ns as _time_ns
except ImportError:
    # In python 3.6 time_ns does not exist.
    from time import time as _time
    def _time_ns():
        return int(_time() * 1_000_000_000)

from .core import Entity



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
    return \
        v is not None and \
        isinstance(v, Entity) and \
        hasattr(v, "_ref") and \
        type(v._ref) == int and \
        v._ref > 0


def duration(*, weeks: float = 0, days: float = 0, hours: float = 0, minutes: float = 0, seconds: float = 0,
             milliseconds: float = 0, microseconds: float = 0, nanoseconds: int = 0) -> int:
    """Durations are always expressed in nanoseconds in DDS (dds_duration_t). This helper function lets
    you write time in a human readable format.

    Examples
    --------
    >>> duration(weeks=2, days=10, minutes=10)

    Parameters
    ----------
        weeks: float, default=0
        days: float, default=0
        hours: float, default=0
        minutes: float, default=0
        seconds: float, default=0
        milliseconds: float, default=0
        microseconds: float, default=0
        nanoseconds: int, default=0

    Returns
    -------
    int
        Duration expressed in nanoseconds.
    """

    days += weeks * 7
    hours += days * 24
    minutes += hours * 60
    seconds += minutes * 60
    milliseconds += seconds * 1000
    microseconds += milliseconds * 1000
    nanoseconds += microseconds * 1000
    return int(nanoseconds)


class timestamp:
    @staticmethod
    def now():
        return _time_ns()
