def duration(*, weeks: float = 0, days: float = 0, hours: float = 0, minutes: float = 0, seconds: float = 0,
             milliseconds: float = 0, microseconds: float = 0, nanoseconds: int = 0) -> int:
    """Durations are always expressed in nanoseconds in DDS (dds_duration_t)

    Args:
        weeks (int, optional): Defaults to 0.
        days (int, optional): Defaults to 0.
        hours (int, optional): Defaults to 0.
        minutes (int, optional): Defaults to 0.
        seconds (int, optional): Defaults to 0.
        milliseconds (int, optional): Defaults to 0.
        microseconds (int, optional): Defaults to 0.
        nanoseconds (int, optional): Defaults to 0.
    """
    days += weeks * 7
    hours += days * 24
    minutes += hours * 60
    seconds += minutes * 60
    milliseconds += seconds * 1000
    microseconds += milliseconds * 1000
    nanoseconds += microseconds * 1000
    return int(nanoseconds)
