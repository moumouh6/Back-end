from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import Annotated, List, Optional
from pydantic import ValidationError
import os

from database import get_db, engine
from models.user import User, Base, UserType
from models.course import Course, CourseMaterial, CourseType, CourseStatus, MaterialType
from schemas import (
    UserCreate, User as UserSchema, Token,
    UserLogin, CourseCreate, Course as CourseSchema,
    CourseMaterial as CourseMaterialSchema, CourseUpdate
)
from auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY,
    ALGORITHM
)
from jose import JWTError, jwt
from utils import save_uploaded_file

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello Coders! Welcome to our Learning Platform"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

@app.post("/register", response_model=UserSchema)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Verify password match
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        nom=user.nom,
        prenom=user.prenom,
        departement=user.departement,
        fonction=user.fonction,
        type_utilisateur=user.type_utilisateur,
        email=user.email,
        telephone=user.telephone,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: UserLogin,
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserSchema)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user

# Course endpoints
@app.post("/courses/", response_model=CourseSchema)
def create_course(
    current_user: Annotated[User, Depends(get_current_user)],
    title: str = Form(...),
    description: str = Form(...),
    course_type: CourseType = Form(...),
    start_datetime: datetime = Form(...),
    end_datetime: datetime = Form(...),
    meeting_link: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    # Verify user is a professor
    if current_user.type_utilisateur != UserType.PROF:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only professors can create courses"
        )
    
    # Verify meeting link is provided for online courses
    if course_type == CourseType.EN_LIGNE and not meeting_link:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Meeting link is required for online courses"
        )
    
    # Handle image upload
    image_path = None
    if image:
        image_path = save_uploaded_file(image, "course_images")
    
    # Create course
    db_course = Course(
        title=title,
        description=description,
        course_type=course_type,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        meeting_link=meeting_link,
        instructor_id=current_user.id,
        image_path=image_path,
        status=CourseStatus.EN_ATTENTE
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@app.get("/courses/", response_model=List[CourseSchema])
def get_courses(
    status: Optional[CourseStatus] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(Course)
    if status:
        query = query.filter(Course.status == status)
    courses = query.offset(skip).limit(limit).all()
    return courses

@app.get("/courses/{course_id}", response_model=CourseSchema)
def get_course(
    course_id: int,
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@app.patch("/courses/{course_id}/status", response_model=CourseSchema)
def update_course_status(
    course_id: int,
    course_update: CourseUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    # Verify user is RH
    if current_user.type_utilisateur != UserType.RH:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only RH can update course status"
        )
    
    course = db.query(Course).filter(Course.id == course_id).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    
    course.status = course_update.status
    db.commit()
    db.refresh(course)
    return course

@app.get("/calendar", response_model=List[CourseSchema])
def get_calendar(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Course).filter(Course.status == CourseStatus.APPROUVE)
    
    if start_date:
        query = query.filter(Course.start_datetime >= start_date)
    if end_date:
        query = query.filter(Course.end_datetime <= end_date)
    
    return query.all()

@app.post("/courses/{course_id}/materials/", response_model=CourseMaterialSchema)
def upload_course_material(
    course_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    title: str = Form(...),
    description: Optional[str] = Form(None),
    material_type: MaterialType = Form(...),
    department: Optional[str] = Form(None),
    is_public: bool = Form(True),
    external_link: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    # Verify course exists and user is the instructor
    course = db.query(Course).filter(Course.id == course_id).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to upload materials to this course")
    
    # Handle file upload or external link
    file_path = None
    if file:
        file_path = save_uploaded_file(file, course_id)
    elif material_type == MaterialType.VIDEO and not external_link:
        raise HTTPException(
            status_code=400,
            detail="External link is required for video materials"
        )
    
    # Create course material record
    db_material = CourseMaterial(
        course_id=course_id,
        title=title,
        description=description,
        material_type=material_type,
        file_path=file_path,
        external_link=external_link,
        department=department,
        is_public=is_public
    )
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material

@app.get("/courses/{course_id}/materials/", response_model=List[CourseMaterialSchema])
def get_course_materials(
    course_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Get materials based on user type and permissions
    query = db.query(CourseMaterial).filter(CourseMaterial.course_id == course_id)
    
    if current_user.type_utilisateur == UserType.ETUDIANT:
        # Students can only see public materials or materials for their department
        query = query.filter(
            (CourseMaterial.is_public == True) |
            (CourseMaterial.department == current_user.departement)
        )
    elif current_user.type_utilisateur == UserType.PROF:
        # Professors can only see materials for their courses
        if course.instructor_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to view materials for this course"
            )
    
    return query.all()

@app.get("/dashboard/materials", response_model=List[CourseMaterialSchema])
def get_dashboard_materials(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    query = db.query(CourseMaterial)
    
    if current_user.type_utilisateur == UserType.ETUDIANT:
        # Students see materials for their department
        query = query.filter(
            (CourseMaterial.is_public == True) |
            (CourseMaterial.department == current_user.departement)
        )
    elif current_user.type_utilisateur == UserType.PROF:
        # Professors see materials for their courses
        query = query.join(Course).filter(Course.instructor_id == current_user.id)
    # RH can see all materials
    
    return query.all()
