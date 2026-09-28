from core.tasks import TaskCore
from models.exceptions import TaskError
from models.task import TaskStatus, TaskType
from models.user import User


def show_board(core):
    print()
    for row in core.board_snapshot():
        print(f"  [{row['type']:<7}] {row['title']:<14} {row['status']:<12} -> {row['assignee']}")
    print()


def try_it(label, action):
    try:
        action()
        print(f"  ok        {label}")
    except TaskError as e:
        print(f"  blocked   {label}")
        print(f"            {e}")


if __name__ == "__main__":
    core = TaskCore()
    db = User(id='u1', name='DB', email='db@board.com')
    riya = User(id='u2', name='Riya', email='riya@board.com')

    feature = core.create_task(TaskType.FEATURE, "Login page", db)
    bug = core.create_task(TaskType.BUG, "Session leak", db)
    story = core.create_task(TaskType.STORY, "Onboarding", db)

    for task in (feature, bug, story):
        core.assign_task(task.id, db)

    print("Welcome to My Tasks Board")
    show_board(core)

    print("state machine")
    try_it("feature open -> resolved", lambda: core.update_task_status(feature.id, TaskStatus.RESOLVED))
    try_it("feature open -> in progress", lambda: core.update_task_status(feature.id, TaskStatus.IN_PROGRESS))
    try_it("feature in progress -> resolved", lambda: core.update_task_status(feature.id, TaskStatus.RESOLVED))
    try_it("feature resolved -> open", lambda: core.update_task_status(feature.id, TaskStatus.OPEN))
    try_it("bug open -> resolved", lambda: core.update_task_status(bug.id, TaskStatus.RESOLVED))
    try_it("story open -> resolved", lambda: core.update_task_status(story.id, TaskStatus.RESOLVED))

    print("\nassignment")
    orphan = core.create_task(TaskType.BUG, "Nobody's bug", db)
    try_it("start an unassigned task", lambda: core.update_task_status(orphan.id, TaskStatus.IN_PROGRESS))
    try_it("assign a task that does not exist", lambda: core.assign_task("made-up-id", db))
    try_it("create an unsupported type", lambda: core.create_task("epic", "Big thing", db))

    print("\ncapacity, limit is 3")
    for i in range(4):
        task = core.create_task(TaskType.BUG, f"Queue bug {i + 1}", db)
        core.assign_task(task.id, db)
        try_it(f"start queue bug {i + 1}", lambda t=task: core.update_task_status(t.id, TaskStatus.IN_PROGRESS))

    print("\nhanding work over")
    busy = core.get_tasks_by_user(db.id)
    moving = [t for t in busy if t.task_status == TaskStatus.IN_PROGRESS][0]
    print(f"  moving '{moving.title}' from DB to Riya")
    core.assign_task(moving.id, riya)
    print(f"  DB now holds   {len(core.get_tasks_by_user(db.id))} tasks")
    print(f"  Riya now holds {len(core.get_tasks_by_user(riya.id))} tasks")

    show_board(core)
