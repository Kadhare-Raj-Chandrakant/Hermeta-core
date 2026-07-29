class ExecutionError(Exception):
    pass


class NoHandlerError(ExecutionError):
    pass


class ActionExecutionError(ExecutionError):
    pass
