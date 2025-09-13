from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseTable
from ..enums import ItemType


class Item(BaseTable):
    __tablename__ = "items"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    item_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default=ItemType.COURSE
    )
    start_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    registrations = relationship("Registration", back_populates="item")
