from sqlalchemy.orm import Session
from sqlalchemy import and_

from edu_register_api.models.user import User
from . import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: Session):
        super().__init__(session, User)

    def get_by_email(self, email: str) -> User | None:
        return (
            self.session.query(self.model)
            .filter(and_(self.model.email == email, self.model.deleted_at.is_(None)))
            .first()
        )

    def email_exists(self, email: str) -> bool:
        return self.get_by_email(email) is not None
