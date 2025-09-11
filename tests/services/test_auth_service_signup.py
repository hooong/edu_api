import pytest
from unittest.mock import Mock, patch

from edu_register_api.services.auth_service import AuthService
from edu_register_api.core.erros import ConflictError
from edu_register_api.schemas.auth import SignupRequest
from edu_register_api.models.user import User


class TestAuthServiceSignup:
    @pytest.fixture
    def mock_uow(self):
        uow = Mock()
        uow.user_repository = Mock()
        return uow

    @pytest.fixture
    def auth_service(self, mock_uow):
        return AuthService(mock_uow)

    @pytest.fixture
    def signup_request(self):
        return SignupRequest(email="test@example.com", password="password123")

    @pytest.fixture
    def mock_user(self):
        user = Mock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        user.hashed_password = "hashed_password123"
        return user

    def test_signup_success(self, auth_service, mock_uow, signup_request, mock_user):
        # Given
        mock_uow.user_repository.email_exists.return_value = False
        mock_uow.user_repository.save.return_value = mock_user

        with patch("edu_register_api.models.user.User.create") as mock_create:
            mock_create.return_value = mock_user

            # When
            result = auth_service.signup(signup_request)

            # Then
            assert result == 1
            mock_uow.user_repository.email_exists.assert_called_once_with(
                email="test@example.com"
            )
            mock_create.assert_called_once_with(
                email="test@example.com", password="password123"
            )
            mock_uow.user_repository.save.assert_called_once_with(mock_user)

    def test_signup_email_already_exists(self, auth_service, mock_uow, signup_request):
        # Given
        mock_uow.user_repository.email_exists.return_value = True

        # When & Then
        with pytest.raises(ConflictError) as exc_info:
            auth_service.signup(signup_request)

        assert "이미 존재하는 이메일입니다." in str(exc_info.value)
        mock_uow.user_repository.email_exists.assert_called_once_with(
            email="test@example.com"
        )
        mock_uow.user_repository.save.assert_not_called()
