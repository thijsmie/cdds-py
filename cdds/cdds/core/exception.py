"""Handle common exception patterns"""

DDS_RETCODE_OK = 0  # Success
DDS_RETCODE_ERROR = -1  # Non specific error
DDS_RETCODE_UNSUPPORTED = -2  # Feature unsupported
DDS_RETCODE_BAD_PARAMETER = -3  # Bad parameter value
DDS_RETCODE_PRECONDITION_NOT_MET = -4  # Precondition for operation not met
DDS_RETCODE_OUT_OF_RESOURCES = -5  # When an operation fails because of a lack of resources
DDS_RETCODE_NOT_ENABLED = -6  # When a configurable feature is not enabled
DDS_RETCODE_IMMUTABLE_POLICY = -7  # When an attempt is made to modify an immutable policy
DDS_RETCODE_INCONSISTENT_POLICY = -8  # When a policy is used with inconsistent values
DDS_RETCODE_ALREADY_DELETED = -9  # When an attempt is made to delete something more than once
DDS_RETCODE_TIMEOUT = -10  # When a timeout has occurred
DDS_RETCODE_NO_DATA = -11  # When expected data is not provided
DDS_RETCODE_ILLEGAL_OPERATION = -12  # When a function is called when it should not be
DDS_RETCODE_NOT_ALLOWED_BY_SECURITY = -13  # When credentials are not enough to use the function


error_message_mapping = {
    DDS_RETCODE_OK: ("DDS_RETCODE_OK", "Success"),
    DDS_RETCODE_ERROR: ("DDS_RETCODE_ERROR", "Non specific error"),
    DDS_RETCODE_UNSUPPORTED: ("DDS_RETCODE_UNSUPPORTED", "Feature unsupported"),
    DDS_RETCODE_BAD_PARAMETER: ("DDS_RETCODE_BAD_PARAMETER", "Bad parameter value"),
    DDS_RETCODE_PRECONDITION_NOT_MET: ("DDS_RETCODE_PRECONDITION_NOT_MET", "Precondition for operation not met"),
    DDS_RETCODE_OUT_OF_RESOURCES: ("DDS_RETCODE_OUT_OF_RESOURCES", "Operation failed because of a lack of resources"),
    DDS_RETCODE_NOT_ENABLED: ("DDS_RETCODE_NOT_ENABLED", "A configurable feature is not enabled"),
    DDS_RETCODE_IMMUTABLE_POLICY: ("DDS_RETCODE_IMMUTABLE_POLICY", "An attempt was made to modify an immutable policy"),
    DDS_RETCODE_INCONSISTENT_POLICY: ("DDS_RETCODE_INCONSISTENT_POLICY", "A policy with inconsistent values was used"),
    DDS_RETCODE_ALREADY_DELETED: ("DDS_RETCODE_ALREADY_DELETED", "An attempt was made to delete something more than once"),
    DDS_RETCODE_TIMEOUT: ("DDS_RETCODE_TIMEOUT", "A timeout has occurred"),
    DDS_RETCODE_NO_DATA: ("DDS_RETCODE_NO_DATA", "Expected data is not provided"),
    DDS_RETCODE_ILLEGAL_OPERATION: ("DDS_RETCODE_ILLEGAL_OPERATION", "A function was called when it should not be"),
    DDS_RETCODE_NOT_ALLOWED_BY_SECURITY:
        ("DDS_RETCODE_NOT_ALLOWED_BY_SECURITY", "Insufficient credentials supplied to use the function")
}


class DDSException(Exception):
    """This exception is thrown when a return code from the underlying C api indicates non-valid use of the API. 
    Print the exception directly or convert it to string for a detailed description. 

    Attributes
    ----------
    code: int
        One of the ``DDS_RETCODE_`` constants that indicates the type of error.
    msg: str
        A human readable description of where the error occurred
    """  

    def __init__(self, code, msg=None, *args, **kwargs):
        self.code = code
        self.msg = msg or ""
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        if self.code in error_message_mapping:
            msg = error_message_mapping[self.code]
            return f"[{msg[0]}] {msg[1]}. {self.msg}"
        else:
            return f"[DDSException] Got an unexpected error code '{self.code}'. {self.msg}"

    def __repr__(self) -> str:
        return str(self)


class DDSAPIException(Exception):
    """This exception is thrown when misuse of the Python API is detected that are not explicitly bound to 
    any C API functions.

    Attributes
    ----------
    msg: str
        A human readable description of what went wrong.
    """
    
    def __init__(self, msg):
        self.msg = msg
        super().__init__()

    def __str__(self) -> str:
        return f"[DDSAPIException] {self.msg}"
