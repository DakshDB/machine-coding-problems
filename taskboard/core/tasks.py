from collections import defaultdict
from uuid import uuid4

from models.constant import MAX_IN_PROGRESS_TASK_PER_USER
from models.exceptions import (
    CapacityExceededError,
    TaskError,
    TaskNotFoundError,
    UnknownTaskTypeError,
)
from models.task import BugTask, FeatureTask, StoryTask, Task, TaskStatus, TaskType
from models.user import User

TASK_REGISTRY = {
    TaskType.FEATURE: FeatureTask,
    TaskType.BUG: BugTask,
    TaskType.STORY: StoryTask,
}


class TaskCore:

    def __init__(self):
        self.tasks: dict[str, Task] = {}
        self.user_tasks: dict[str, set[str]] = defaultdict(set)

    def create_task(self, task_type: TaskType, title: str, creator: User) -> Task:
        task_class = TASK_REGISTRY.get(task_type)
        if task_class is None:
            raise UnknownTaskTypeError(f"don't know how to build a {task_type} task")

        task = task_class(
            id=str(uuid4()),
            title=title,
            creator=creator,
        )
        self.tasks[task.id] = task
        return task

    def assign_task(self, task_id: str, assignee: User):
        task = self._get_task(task_id)
        if assignee is None:
            raise TaskError("assignee is required")

        if task.assignee and task.assignee.id == assignee.id:
            return

        if task.task_status == TaskStatus.IN_PROGRESS:
            self._check_capacity(assignee.id)

        if task.assignee:
            self.user_tasks[task.assignee.id].discard(task_id)

        task.assignee = assignee
        self.user_tasks[assignee.id].add(task_id)

    def update_task_status(self, task_id: str, status: TaskStatus):
        task = self._get_task(task_id)

        if status == TaskStatus.IN_PROGRESS:
            if task.assignee is None:
                raise TaskError("task has to be assigned before it can be started")
            self._check_capacity(task.assignee.id, ignore_task_id=task_id)

        task.update_status(status)

    def get_tasks_by_user(self, user_id: str) -> list[Task]:
        return [self.tasks[task_id] for task_id in self.user_tasks.get(user_id, set())]

    def board_snapshot(self) -> list[dict]:
        return [task.to_dict() for task in self.tasks.values()]

    def _get_task(self, task_id: str) -> Task:
        task = self.tasks.get(task_id)
        if task is None:
            raise TaskNotFoundError(f"no task with id {task_id}")
        return task

    def _check_capacity(self, user_id: str, ignore_task_id: str = None):
        in_progress = 0
        for task_id in self.user_tasks.get(user_id, set()):
            if task_id == ignore_task_id:
                continue
            if self.tasks[task_id].task_status == TaskStatus.IN_PROGRESS:
                in_progress += 1

        if in_progress >= MAX_IN_PROGRESS_TASK_PER_USER:
            raise CapacityExceededError(
                f"{user_id} already has {in_progress} tasks in progress, "
                f"limit is {MAX_IN_PROGRESS_TASK_PER_USER}"
            )
