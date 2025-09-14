from datetime import datetime, timezone

from sqlalchemy import Integer, ForeignKey, DateTime, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from edu_register_api.core.erros import ConflictError
from edu_register_api.enums import RegistrationStatus
from edu_register_api.models import BaseTable


class Registration(BaseTable):
    __tablename__ = "registrations"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("items.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=RegistrationStatus.PENDING.value,
        server_default=text(f"'{RegistrationStatus.PENDING.value}'"),
    )
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    item = relationship("Item", back_populates="registrations")
    user = relationship("User", back_populates="registrations")
    payment = relationship("Payment", back_populates="registration")

    @property
    def is_completable(self) -> bool:
        return self.status == RegistrationStatus.PAID

    def complete(self) -> None:
        if not self.is_completable:
            raise ConflictError("완료 처리가 불가능한 상태입니다.")

        self.completed_at = datetime.now(timezone.utc)
        self.status = RegistrationStatus.COMPLETED.value

    def paid(self) -> None:
        if not self.status == RegistrationStatus.PENDING:
            raise ConflictError("결제 완료 처리가 불가능한 상태입니다.")

        self.status = RegistrationStatus.PAID.value
