from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Session, select
from app.models import User
from app.database import engine, get_session
from app.schemas import UserCreate, UserRead, Token
from app.auth import hash_password, verify_password, create_access_token

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API de la plateforme e-learning"}


@app.on_event("startup")
def startup():
    SQLModel.metadata.create_all(engine)

@app.post("/SignIn", response_model=UserRead)
def register(user: UserCreate, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.email == user.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    db_user = User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password),
        role=user.role
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@app.post("/login", response_model=Token)
def login(user: UserCreate, session: Session = Depends(get_session)):
    db_user = session.exec(select(User).where(User.email == user.email)).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Identifiants invalides")
    
    token = create_access_token(data={"sub": db_user.email, "role": db_user.role})
    return {"access_token": token, "token_type": "bearer"}

