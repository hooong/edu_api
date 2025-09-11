from unittest.mock import Mock, patch
import pytest

from edu_register_api.core.erros import NotFoundError, UnauthorizedError
from edu_register_api.models.user import User
from edu_register_api.schemas.auth import LoginRequest
from edu_register_api.services.auth_service import AuthService


class TestAuthServiceLogin:
    @pytest.fixture
    def mock_uow(self):
        uow = Mock()
        uow.user_repository = Mock()
        return uow

    @pytest.fixture
    def auth_service(self, mock_uow):
        return AuthService(mock_uow)

    @pytest.fixture
    def login_request(self):
        return LoginRequest(email="test@example.com", password="password123")

    @pytest.fixture
    def mock_user(self):
        user = Mock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        user.hashed_password = "hashed_password123"
        return user

    def test_login_success(self, auth_service, mock_uow, login_request, mock_user):
        # Given
        mock_uow.user_repository.get_by_email.return_value = mock_user

        with (
            patch(
                "edu_register_api.services.auth_service.verify_password"
            ) as mock_verify,
            patch(
                "edu_register_api.services.auth_service.create_access_token"
            ) as mock_create_token,
        ):
            mock_verify.return_value = True
            mock_create_token.return_value = "test_access_token"

            # When
            result = auth_service.login(login_request)

            # Then
            assert result == "test_access_token"

            mock_uow.user_repository.get_by_email.assert_called_once_with(
                "test@example.com"
            )
            mock_verify.assert_called_once_with("password123", "hashed_password123")
            mock_create_token.assert_called_once_with(sub="1")

    def test_login_user_not_found(self, auth_service, mock_uow, login_request):
        # Given
        mock_uow.user_repository.get_by_email.return_value = None

        # When & Then
        with pytest.raises(NotFoundError) as exc_info:
            auth_service.login(login_request)

        assert "존재하지 않는 사용자입니다." in str(exc_info.value)
        mock_uow.user_repository.get_by_email.assert_called_once_with(
            "test@example.com"
        )

    def test_login_invalid_password(
        self, auth_service, mock_uow, login_request, mock_user
    ):
        # Given
        mock_uow.user_repository.get_by_email.return_value = mock_user

        with patch(
            "edu_register_api.services.auth_service.verify_password"
        ) as mock_verify:
            mock_verify.return_value = False

            # When & Then
            with pytest.raises(UnauthorizedError) as exc_info:
                auth_service.login(login_request)

            assert "이메일 또는 비밀번호가 올바르지 않습니다." in str(exc_info.value)
            mock_uow.user_repository.get_by_email.assert_called_once_with(
                "test@example.com"
            )
            mock_verify.assert_called_once_with("password123", "hashed_password123")
