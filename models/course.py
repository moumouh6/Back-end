from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .user import Base

class CourseType(enum.Enum):
    PRESENTIEL = "presentiel"
    EN_LIGNE = "en_ligne"

class CourseStatus(enum.Enum):
    EN_ATTENTE = "en_attente"
    APPROUVE = "approuve"
    REFUSE = "refuse"

class MaterialType(enum.Enum):
    VIDEO = "video"
    PDF = "pdf"
    DOCUMENT = "document"
    LIEN = "lien"

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    instructor_id = Column(Integer, ForeignKey("users.id"))
    course_type = Column(Enum(CourseType))
    start_datetime = Column(DateTime)
    end_datetime = Column(DateTime)
    meeting_link = Column(String, nullable=True)  # Lien pour les cours en ligne
    image_path = Column(String, nullable=True)
    status = Column(Enum(CourseStatus), default=CourseStatus.EN_ATTENTE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with User
    instructor = relationship("User", back_populates="courses")
    
    # Course materials will be stored as files in a directory
    materials = relationship("CourseMaterial", back_populates="course")

class CourseMaterial(Base):
    __tablename__ = "course_materials"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    title = Column(String)  # Titre du matériel
    description = Column(Text, nullable=True)  # Description du matériel
    material_type = Column(Enum(MaterialType))  # Type de matériel
    file_path = Column(String, nullable=True)  # Chemin du fichier pour les fichiers uploadés
    external_link = Column(String, nullable=True)  # Lien externe pour les vidéos pré-enregistrées
    department = Column(String, nullable=True)  # Département spécifique (si null, visible par tous)
    is_public = Column(Boolean, default=True)  # Si le matériel est public ou privé
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    course = relationship("Course", back_populates="materials") 