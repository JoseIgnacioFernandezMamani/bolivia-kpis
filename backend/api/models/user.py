import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, func
from database import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    editor = "editor"
    public = "public"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.public, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    google_id = Column(String(255), nullable=True, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
