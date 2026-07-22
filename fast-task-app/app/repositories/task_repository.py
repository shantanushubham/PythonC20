from sqlalchemy.orm import Session

from app.models.task import Task


class TaskRepository:

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, task: Task) -> Task:
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_by_user(self, user_id: int) -> list[Task]:
        return (
            self.db.query(Task)
            .filter(Task.user_id == user_id)
            .order_by(Task.due_date.asc())
            .all()
        )

    def get_by_id_and_user(self, task_id: int, user_id: int) -> Task | None:
        return (
            self.db.query(Task)
            .filter(Task.id == task_id, Task.user_id == user_id)
            .first()
        )

    def update(self, task: Task) -> Task:
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        self.db.delete(task)
        self.db.commit()
