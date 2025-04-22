from sqlalchemy import Column, Integer, String, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

class UserType(enum.Enum):
    ETUDIANT = "etudiant"
    PROF = "prof"
    RH = "rh"

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String)
    prenom = Column(String)
    departement = Column(String)
    fonction = Column(String)
    type_utilisateur = Column(Enum(UserType))
    email = Column(String, unique=True, index=True)
    telephone = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    
    # Relationship with Course
    courses = relationship("Course", back_populates="instructor") 