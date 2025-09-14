from sqlalchemy import and_
from sqlalchemy.orm import Session

from edu_register_api.enums import ItemType
from edu_register_api.models import Item
from edu_register_api.repositories import BaseRepository


class ItemRepository(BaseRepository[Item]):
    def __init__(self, session: Session):
        super().__init__(session, Item)

    def get_by_id_and_item_type(self, id: int, item_type: ItemType) -> Item | None:
        return (
            self.session.query(self.model)
            .filter(
                and_(
                    self.model.id == id,
                    self.model.item_type == item_type,
                    self.model.deleted_at.is_(None),
                )
            )
            .first()
        )
