from pydantic import BaseModel, EmailStr, constr, HttpUrl
from typing import Optional, List
from datetime import datetime
from models.user import UserType
from models.course import CourseType, CourseStatus, MaterialType

class UserBase(BaseModel):
    nom: str
    prenom: str
    departement: str
    fonction: str
    type_utilisateur: UserType
    email: EmailStr
    telephone: str

class UserCreate(UserBase):
    password: str
    confirm_password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Course schemas
class CourseBase(BaseModel):
    title: str
    description: str
    course_type: CourseType
    start_datetime: datetime
    end_datetime: datetime
    meeting_link: Optional[str] = None

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    status: CourseStatus

# Course Material schemas
class CourseMaterialBase(BaseModel):
    title: str
    description: Optional[str] = None
    material_type: MaterialType
    department: Optional[str] = None
    is_public: bool = True

class CourseMaterialCreate(CourseMaterialBase):
    external_link: Optional[str] = None

class CourseMaterial(CourseMaterialBase):
    id: int
    course_id: int
    file_path: Optional[str] = None
    external_link: Optional[str] = None
    uploaded_at: datetime

    class Config:
        from_attributes = True

class Course(CourseBase):
    id: int
    instructor_id: int
    instructor: User
    image_path: Optional[str] = None
    status: CourseStatus
    created_at: datetime
    updated_at: datetime
    materials: List[CourseMaterial] = []

    class Config:
        from_attributes = True 