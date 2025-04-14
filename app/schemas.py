from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models import Role

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[Role] = Role.etudiant

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: Role

class Token(BaseModel):
    access_token: str
    token_type: str