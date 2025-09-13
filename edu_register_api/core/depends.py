from typing import Generator

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from edu_register_api.core.erros import UnauthorizedError
from edu_register_api.core.uow import UnitOfWork
from edu_register_api.core.security import verify_token
from edu_register_api.models.user import User
from edu_register_api.core.database import SessionLocal

from edu_register_api.schemas.auth import UserInfo
from edu_register_api.services import AuthService

bearer = HTTPBearer()


def get_uow() -> Generator[UnitOfWork, None, None]:
    with UnitOfWork(SessionLocal) as uow:
        yield uow


def get_auth_service(uow: UnitOfWork = Depends(get_uow)) -> AuthService:
    return AuthService(uow)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    uow: UnitOfWork = Depends(get_uow),
) -> UserInfo:
    try:
        token = credentials.credentials
        payload = verify_token(token)
        user_id: int = int(payload.get("sub"))
    except ValueError as e:
        raise UnauthorizedError(str(e))

    user: User | None = uow.user_repository.get_by_id(user_id)

    if user is None:
        raise UnauthorizedError(detail="사용자를 찾을 수 없습니다.")

    return UserInfo(id=user_id, email=user.email)
