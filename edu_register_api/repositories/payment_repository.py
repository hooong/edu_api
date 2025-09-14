from sqlalchemy.orm import Session

from edu_register_api.models import Payment
from edu_register_api.repositories import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, session: Session):
        super().__init__(session, Payment)
