from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.api.auth import router as auth_router
from app.api.external import router as external_router
from app.api.tasks import router as tasks_router

from app.core.database import get_db

app = FastAPI()
app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(external_router)


@app.get("/")
def home(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))

    return {"message": "Database Connected"}
