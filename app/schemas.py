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


from pydantic import BaseModel
from typing import Optional

class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    file: Optional[str] = None

class CourseCreate(CourseBase):
    teacher_id: int

class CourseUpdate(CourseBase):
    pass

class Course(CourseBase):
    id: int
    teacher_id: int

    class Config:
        orm_mode = True
