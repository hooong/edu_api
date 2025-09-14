from datetime import datetime, timezone
from sqlalchemy import Integer, ForeignKey, String, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseTable
from ..core.erros import ConflictError
from ..enums import PaymentStatus


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

    def cancel(self) -> None:
        if self.status != PaymentStatus.PAID:
            raise ConflictError("결제 취소가 불가능한 상태입니다.")

        self.status = PaymentStatus.CANCELED.value
        self.cancelled_at = datetime.now(timezone.utc)
