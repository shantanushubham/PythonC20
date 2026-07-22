from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.user import UserRole


class UserReponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: UserRole

    model_config = ConfigDict(from_attributes=True)
