from typing import Self
from pydantic import EmailStr
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from edu_register_api.core.security import get_password_hash
from .base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    registrations = relationship("Registration", back_populates="user")

    @classmethod
    def create(cls, email: EmailStr, password: str) -> Self:
        return cls(email=email, hashed_password=get_password_hash(password=password))
