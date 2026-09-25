from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    password_reset_token = Column(String, nullable=True, index=True)
    password_reset_expires_at = Column(Integer, nullable=True)
    password_reset_requested_at = Column(Integer, nullable=True)

    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
