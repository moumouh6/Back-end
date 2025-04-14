from sqlmodel import SQLModel, Field
from typing import Optional
from enum import Enum

# role definie proprement par enum 
class Role(str , Enum):
    admin = "admin"
    proffesseur = "proffesseur"
    etudiant = "etudiant"


# modele d'etulisaateur 
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    password: str
    role: Role = Role.admin

    