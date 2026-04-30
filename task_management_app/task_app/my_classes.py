import datetime

class Task:

  def __init__(self, id: int, owner: str, title: str, description: str, due_at: datetime.date) -> None:
    self.id = id
    self.owner = owner
    self.title = title
    self.description = description
    self.status = "PENDING"
    self.created_at = datetime.date.today()
    if isinstance(due_at, str):
      due_at = datetime.date.fromisoformat(due_at)
    if (due_at <= self.created_at):
      raise Exception("Please use valid due_at")
    self.due_at = due_at


