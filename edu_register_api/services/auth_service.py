from edu_register_api.core.erros import ConflictError
from edu_register_api.models.user import User
from edu_register_api.repositories.user_repository import UserRepository
from edu_register_api.core.decorators import transactional
from edu_register_api.schemas.auth import SignupRequest


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
