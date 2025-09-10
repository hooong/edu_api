from datetime import datetime
from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel


class CourseRegistration(BaseModel):
    __tablename__ = "course_registrations"

    course_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("courses.id"), nullable=False
    )
    registration_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("registrations.id"), nullable=False
    )
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    course = relationship("Course", back_populates="course_registrations")
    registration = relationship("Registration", back_populates="course_registration")
