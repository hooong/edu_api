from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    registrations = relationship("Registration", back_populates="user")
