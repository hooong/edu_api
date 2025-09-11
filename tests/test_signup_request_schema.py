import pytest
from pydantic import ValidationError

from edu_register_api.schemas.auth import SignupRequest


class TestSignupRequestSchema:
    def test_signup_request_success(self):
        # Given
        valid_data = {"email": "test@example.com", "password": "password123"}

        # When
        request = SignupRequest(**valid_data)

        # Then
        assert request.email == "test@example.com"
        assert request.password == "password123"

    def test_signup_request_missing_email(self):
        # Given
        invalid_data = {"password": "password123"}

        # When & Then
        with pytest.raises(ValidationError) as exc_info:
            SignupRequest(**invalid_data)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"
        assert errors[0]["loc"] == ("email",)

    def test_signup_request_missing_password(self):
        # Given
        invalid_data = {"email": "test@example.com"}

        # When & Then
        with pytest.raises(ValidationError) as exc_info:
            SignupRequest(**invalid_data)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"
        assert errors[0]["loc"] == ("password",)

    def test_signup_request_empty_email(self):
        # Given
        invalid_data = {"email": "", "password": "password123"}

        # When & Then
        with pytest.raises(ValidationError) as exc_info:
            SignupRequest(**invalid_data)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "value_error"

    def test_signup_request_invalid_email_format(self):
        # Given
        invalid_data = {"email": "invalid-email", "password": "password123"}

        # When & Then
        with pytest.raises(ValidationError) as exc_info:
            SignupRequest(**invalid_data)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "value_error"
        assert errors[0]["loc"] == ("email",)
