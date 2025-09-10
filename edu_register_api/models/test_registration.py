from datetime import datetime
from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel


class TestRegistration(BaseModel):
    __tablename__ = "test_registrations"

    test_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tests.id"), nullable=False
    )
    registration_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("registrations.id"), nullable=False
    )
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    test = relationship("Test", back_populates="test_registrations")
    registration = relationship("Registration", back_populates="test_registration")
