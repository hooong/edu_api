from datetime import datetime
from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from edu_register_api.models import BaseTable


class Registration(BaseTable):
    __tablename__ = "registrations"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("items.id"), nullable=False
    )
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    item = relationship("Item", back_populates="registrations")
    user = relationship("User", back_populates="registrations")
