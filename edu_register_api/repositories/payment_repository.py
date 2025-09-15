from datetime import date, datetime

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session, joinedload

from edu_register_api.enums import PaymentStatusFilter
from edu_register_api.models import Payment, Registration, Item
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

    def get_user_payments_with_pagination(
        self,
        user_id: int,
        start_date: date,
        end_date: date,
        page: int = 1,
        size: int = 10,
        payment_status: PaymentStatusFilter | None = None,
    ) -> tuple[list[Payment], int]:
        query = (
            self.session.query(self.model)
            .join(Registration, self.model.registration_id == Registration.id)
            .join(Item, Registration.item_id == Item.id)
            .options(joinedload(self.model.registration).joinedload(Registration.item))
            .filter(
                and_(
                    Registration.user_id == user_id,
                    self.model.deleted_at.is_(None),
                )
            )
        )

        if payment_status:
            query = query.filter(self.model.status == payment_status.value)

        if start_date:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            query = query.filter(self.model.paid_at >= start_datetime)
        if end_date:
            end_datetime = datetime.combine(end_date, datetime.max.time())
            query = query.filter(self.model.paid_at <= end_datetime)

        total = query.count()

        payments = (
            query.order_by(desc(self.model.created_at))
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )

        return payments, total
