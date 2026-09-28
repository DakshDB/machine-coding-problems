class TaskError(Exception):
    pass


class TaskNotFoundError(TaskError):
    pass


class UnknownTaskTypeError(TaskError):
    pass


class InvalidTransitionError(TaskError):
    pass


class CapacityExceededError(TaskError):
    pass
