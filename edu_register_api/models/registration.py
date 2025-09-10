from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel


class Registration(BaseModel):
    __tablename__ = "registrations"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False)

    user = relationship("User", back_populates="registrations")
    test_registration = relationship(
        "TestRegistration", back_populates="registration", uselist=False
    )
    course_registration = relationship(
        "CourseRegistration", back_populates="registration", uselist=False
    )
    payments = relationship("Payment", back_populates="registration")
