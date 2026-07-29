class AdapterError(Exception):
    pass


class InvalidAdapterTaskError(AdapterError):
    pass


class AdapterNotReadyError(AdapterError):
    pass
