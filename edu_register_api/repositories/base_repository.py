from abc import ABC
from datetime import datetime, timezone
from typing import TypeVar, Generic, List, Type
from sqlalchemy.orm import Session
from sqlalchemy import and_

from edu_register_api.models import BaseTable

ModelType = TypeVar("ModelType", bound=BaseTable)


class BaseRepository(Generic[ModelType], ABC):
    def __init__(self, session: Session, model: Type[ModelType]):
        self.session = session
        self.model = model

    def get_by_id(self, id: int) -> ModelType | None:
        return (
            self.session.query(self.model)
            .filter(and_(self.model.id == id, self.model.deleted_at.is_(None)))
            .first()
        )

    def get_all(self) -> List[ModelType]:
        return (
            self.session.query(self.model).filter(self.model.deleted_at.is_(None)).all()
        )

    def save(self, obj: ModelType) -> ModelType:
        self.session.add(obj)
        self.session.flush()
        self.session.refresh(obj)
        return obj

    def update(self, obj: ModelType, data: dict) -> ModelType:
        for field, value in data.items():
            if hasattr(obj, field):
                setattr(obj, field, value)

        self.session.add(obj)
        self.session.flush()
        self.session.refresh(obj)
        return obj

    def delete(self, id: int) -> bool:
        obj = self.get_by_id(id)
        if obj:
            obj.deleted_at = datetime.now(timezone.utc)
            self.session.add(obj)
            self.session.flush()
            return True
        return False

    def hard_delete(self, id: int) -> bool:
        obj = self.get_by_id(id)
        if obj:
            self.session.delete(obj)
            self.session.flush()
            return True
        return False

    def exists(self, id: int) -> bool:
        return self.get_by_id(id) is not None
