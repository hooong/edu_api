from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload

from edu_register_api.models import Registration, Item
from edu_register_api.repositories import BaseRepository


class RegistrationRepository(BaseRepository[Registration]):
    def __init__(self, session: Session):
        super().__init__(session, Registration)

    def get_by_item_id_and_user_id(
        self, item_id: int, user_id: int
    ) -> Registration | None:
        return (
            self.session.query(self.model)
            .options(joinedload(self.model.item))
            .filter(
                and_(
                    self.model.item.has(Item.id == item_id),
                    self.model.user_id == user_id,
                    self.model.deleted_at.is_(None),
                )
            )
            .first()
        )
