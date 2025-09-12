from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from edu_register_api.core.erros import UnauthorizedError
from edu_register_api.repositories.user_repository import UserRepository
from edu_register_api.core.security import verify_token
from edu_register_api.models.user import User
from edu_register_api.core.database import get_db
from sqlalchemy.orm import Session

from edu_register_api.schemas.auth import UserInfo

bearer = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> UserInfo:
    try:
        token = credentials.credentials
        payload = verify_token(token)
        user_id: int = int(payload.get("sub"))
    except ValueError as e:
        raise UnauthorizedError(str(e))

    user_repository = UserRepository(db)
    user: User | None = user_repository.get_by_id(user_id)

    if user is None:
        raise UnauthorizedError(detail="사용자를 찾을 수 없습니다.")

    return UserInfo(id=user_id, email=user.email)
