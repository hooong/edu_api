from contextlib import AbstractContextManager
from typing import Self

from sqlalchemy.orm import sessionmaker, Session

from edu_register_api.repositories.user_repository import UserRepository


class UnitOfWork(AbstractContextManager):
    def __init__(self, session_factory: sessionmaker = sessionmaker):
        self.session_factory = session_factory
        self.session: Session | None = None

        self.user_repository: UserRepository | None = None

    def __enter__(self) -> Self:
        self.session = self.session_factory()

        self.user_repository = UserRepository(self.session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()

    def commit(self):
        if self.session:
            self.session.commit()

    def rollback(self):
        if self.session:
            self.session.rollback()
