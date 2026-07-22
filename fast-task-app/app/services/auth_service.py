from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_reporsitory import UserRepository


class AuthService:

    def __init__(self, db: Session) -> None:
        self.user_repository = UserRepository(db)

    def signup(self, full_name: str, email: str, password: str) -> tuple[User, str]:
        existing_user = self.user_repository.get_user_by_email(email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        user = User(
            full_name=full_name, email=email, password_hash=hash_password(password)
        )
        created_user = self.user_repository.create(user)
        token = create_access_token(created_user.id, created_user.role.value)
        return (created_user, token)

    def login(self, email: str, password: str) -> tuple[User, str]:
        user = self.user_repository.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        if not verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_access_token(user.id, user.role.value)
        return user, token
