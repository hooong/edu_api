from datetime import datetime, timezone
from sqlalchemy import DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column

Base = declarative_base()


def utc_now():
    return datetime.now(timezone.utc)


class BaseTable(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now, index=True
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, index=True)
