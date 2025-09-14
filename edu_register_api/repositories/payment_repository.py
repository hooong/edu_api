from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload

from edu_register_api.models import Payment
from edu_register_api.repositories import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, session: Session):
        super().__init__(session, Payment)

    def get_by_id_with_registration(self, id: int) -> Payment | None:
        return (
            self.session.query(self.model)
            .options(joinedload(self.model.registration))
            .filter(and_(self.model.id == id, self.model.deleted_at.is_(None)))
            .first()
        )
