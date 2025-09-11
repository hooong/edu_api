from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from edu_register_api.core.database import get_db
from edu_register_api.services.auth_service import AuthService
from edu_register_api.repositories.user_repository import UserRepository
from edu_register_api.schemas.auth import (
    SignupRequest,
    SignupResponse,
    LoginRequest,
    LoginResponse,
)

router = APIRouter(prefix="", tags=["Auth"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    user_repository = UserRepository(db)
    return AuthService(user_repository)


@router.post(
    "/signup",
    response_model=SignupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="회원가입",
    description="새로운 사용자 계정을 생성합니다.",
    responses={
        409: {"description": "이미 존재하는 이메일"},
    },
)
def signup(
    request: SignupRequest, auth_service: AuthService = Depends(get_auth_service)
) -> SignupResponse:
    user_id: int = auth_service.signup(request)
    return SignupResponse(user_id=user_id)


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="로그인",
    description="이메일과 비밀번호 로그인을 통해 JWT Access Token을 발급합니다.",
    responses={
        401: {"description": "인증 실패"},
        404: {"description": "존재하지 않는 사용자"},
    },
)
def login(
    request: LoginRequest, auth_service: AuthService = Depends(get_auth_service)
) -> LoginResponse:
    access_token = auth_service.login(request)
    return LoginResponse(access_token=access_token)
