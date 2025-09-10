from functools import wraps
from typing import Callable, Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from edu_register_api.repositories import BaseRepository


def transactional(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        service_obj = args[0]  # self
        db_session: Session | None = _find_db_session(service_obj)

        if db_session:
            try:
                if db_session.get_transaction() is not None:
                    return func(*args, **kwargs)

                result = func(*args, **kwargs)
                db_session.commit()
                return result
            except Exception as e:
                db_session.rollback()

                if isinstance(e, HTTPException):
                    raise e

                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return func(*args, **kwargs)

    return wrapper


def _find_db_session(service_obj: Any) -> Session | None:
    if hasattr(service_obj, "repository") and hasattr(
        service_obj.repository, "session"
    ):
        return service_obj.repository.session

    for attr_name in dir(service_obj):
        if attr_name.startswith("_"):
            continue

        attr_value = getattr(service_obj, attr_name)
        if isinstance(attr_value, BaseRepository):
            return attr_value.session

    return None
