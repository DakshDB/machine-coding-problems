from abc import ABC, abstractmethod
from enum import Enum

from models.exceptions import InvalidTransitionError
from models.user import User


class TaskType(Enum):
    FEATURE = 'feature'
    BUG = 'bug'
    STORY = 'story'


class TaskStatus(Enum):
    OPEN = 'open'
    IN_PROGRESS = 'in_progress'
    RESOLVED = 'resolved'
    DELAYED = 'delayed'


class Task(ABC):

    # where each status is allowed to go next. subclasses override only what differs.
    TRANSITIONS = {
        TaskStatus.OPEN: {TaskStatus.IN_PROGRESS, TaskStatus.DELAYED},
        TaskStatus.IN_PROGRESS: {TaskStatus.RESOLVED, TaskStatus.DELAYED},
        TaskStatus.DELAYED: {TaskStatus.OPEN, TaskStatus.IN_PROGRESS},
        TaskStatus.RESOLVED: set(),
    }

    @property
    @abstractmethod
    def task_type(self) -> TaskType:
        ...

    def __init__(self, id: str, title: str, creator: User,
                 assignee: User = None, task_status: TaskStatus = TaskStatus.OPEN):
        self.id = id
        self.title = title
        self.creator = creator
        self.assignee = assignee
        self.task_status = task_status

    def update_status(self, status: TaskStatus):
        if status == self.task_status:
            return

        allowed = self.TRANSITIONS[self.task_status]
        if status not in allowed:
            raise InvalidTransitionError(
                f"a {self.task_type.value} can't go {self.task_status.value} -> {status.value}, "
                f"allowed from here: {sorted(s.value for s in allowed) or 'nothing, it is closed'}"
            )

        self.task_status = status

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "type": self.task_type.value,
            "creator": self.creator.name,
            "assignee": self.assignee.name if self.assignee else None,
            "status": self.task_status.value,
        }


class FeatureTask(Task):
    task_type = TaskType.FEATURE


class StoryTask(Task):
    task_type = TaskType.STORY


class BugTask(Task):
    task_type = TaskType.BUG

    # a bug can be closed straight from open, rest of the table is the same
    TRANSITIONS = {
        **Task.TRANSITIONS,
        TaskStatus.OPEN: {TaskStatus.IN_PROGRESS, TaskStatus.RESOLVED, TaskStatus.DELAYED},
    }
