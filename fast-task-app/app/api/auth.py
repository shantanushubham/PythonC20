from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import AuthResponse, LoginRequest, SignupRequest
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=AuthResponse)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    service = AuthService(db)

    return service.signup(request.full_name, request.email, request.password)


@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user, token = AuthService(db).login(request.email, request.password)

    return {"access_token": token, "user": user}
