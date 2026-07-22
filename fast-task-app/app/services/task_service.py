from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.task import Task, TaskStatus
from app.models.user import User
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:

    def __init__(self, db: Session) -> None:
        self.task_repository = TaskRepository(db)

    def _get_owned_task(self, current_user: User, task_id: int) -> Task:
        task = self.task_repository.get_by_id_and_user(task_id, current_user.id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

    def create_task(self, current_user: User, data: TaskCreate) -> Task:
        task = Task(
            title=data.title,
            description=data.description,
            due_date=data.due_date,
            status=TaskStatus.PENDING,
            user_id=current_user.id,
        )
        return self.task_repository.create(task)

    def list_tasks(self, current_user: User) -> list[Task]:
        return self.task_repository.get_by_user(current_user.id)

    def get_task(self, current_user: User, task_id: int) -> Task:
        return self._get_owned_task(current_user, task_id)

    def update_task(
        self, current_user: User, task_id: int, data: TaskUpdate
    ) -> Task:
        task = self._get_owned_task(current_user, task_id)
        updates = data.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(task, field, value)
        return self.task_repository.update(task)

    def delete_task(self, current_user: User, task_id: int) -> None:
        task = self._get_owned_task(current_user, task_id)
        self.task_repository.delete(task)
