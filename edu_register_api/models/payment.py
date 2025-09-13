from datetime import datetime
from sqlalchemy import Integer, ForeignKey, String, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseTable


class Payment(BaseTable):
    __tablename__ = "payments"

    registration_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("registrations.id"), nullable=False
    )
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    method: Mapped[str] = mapped_column(String(50), nullable=False)
    paid_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    cancelled_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    registration = relationship("Registration", back_populates="payment")
