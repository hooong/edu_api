from edu_register_api.core.erros import ConflictError, NotFoundError, UnauthorizedError
from edu_register_api.models.user import User
from edu_register_api.repositories.user_repository import UserRepository
from edu_register_api.core.decorators import transactional
from edu_register_api.core.security import verify_password, create_access_token
from edu_register_api.schemas.auth import SignupRequest, LoginRequest


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    @transactional
    def signup(self, request: SignupRequest) -> int:
        if self.user_repository.email_exists(email=request.email):
            raise ConflictError("이미 존재하는 이메일입니다.")

        user = User.create(email=request.email, password=request.password)
        self.user_repository.save(user)

        return user.id

    def login(self, request: LoginRequest) -> str:
        user: User | None = self.user_repository.get_by_email(request.email)
        if not user:
            raise NotFoundError("존재하지 않는 사용자입니다.")

        if not verify_password(request.password, user.hashed_password):
            raise UnauthorizedError("이메일 또는 비밀번호가 올바르지 않습니다.")

        access_token = create_access_token(sub=str(user.id))

        return access_token
