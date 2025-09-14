from datetime import datetime, timezone
import pytest

from edu_register_api.core.erros import ConflictError
from edu_register_api.enums import RegistrationStatus
from edu_register_api.models.registration import Registration


class TestRegistration:
    def test_is_completable_when_status_is_pending(self):
        """status가 PENDING일 때 is_completable은 False를 반환해야 한다"""
        # Given
        registration = Registration()
        registration.status = RegistrationStatus.PENDING

        # When
        result = registration.is_completable

        # Then
        assert result is False

    def test_is_completable_when_status_is_paid(self):
        """status가 PAID일 때 is_completable은 True를 반환해야 한다"""
        # Given
        registration = Registration()
        registration.status = RegistrationStatus.PAID

        # When
        result = registration.is_completable

        # Then
        assert result is True

    def test_is_completable_when_status_is_completed(self):
        """status가 COMPLETED일 때 is_completable은 False를 반환해야 한다"""
        # Given
        registration = Registration()
        registration.status = RegistrationStatus.COMPLETED

        # When
        result = registration.is_completable

        # Then
        assert result is False

    def test_is_completed_when_status_is_pending(self):
        """status가 PENDING일 때 is_completed는 False를 반환해야 한다"""
        # Given
        registration = Registration()
        registration.status = RegistrationStatus.PENDING

        # When
        result = registration.is_completed

        # Then
        assert result is False

    def test_is_completed_when_status_is_paid(self):
        """status가 PAID일 때 is_completed는 False를 반환해야 한다"""
        # Given
        registration = Registration()
        registration.status = RegistrationStatus.PAID

        # When
        result = registration.is_completed

        # Then
        assert result is False

    def test_is_completed_when_status_is_completed(self):
        """status가 COMPLETED일 때 is_completed는 True를 반환해야 한다"""
        # Given
        registration = Registration()
        registration.status = RegistrationStatus.COMPLETED

        # When
        result = registration.is_completed

        # Then
        assert result is True

    def test_complete_sets_completed_at_to_current_time(self):
        """complete() 메서드는 completed_at을 현재 시간으로 설정해야 한다"""
        # Given
        registration = Registration()
        registration.status = RegistrationStatus.PAID  # 완료 가능한 상태
        registration.completed_at = None
        before_complete = datetime.now(timezone.utc)

        # When
        registration.complete()
        after_complete = datetime.now(timezone.utc)

        # Then
        assert registration.completed_at is not None
        assert before_complete <= registration.completed_at <= after_complete
        assert registration.completed_at.tzinfo == timezone.utc

    def test_complete_raises_conflict_error_when_not_completable(self):
        """완료 불가능한 상태에서 complete()를 호출하면 ConflictError가 발생해야 한다"""
        # Given
        registration = Registration()
        registration.status = RegistrationStatus.PENDING  # 완료 불가능한 상태

        # When & Then
        with pytest.raises(ConflictError) as exc_info:
            registration.complete()

        assert "완료 처리가 불가능한 상태입니다." in str(exc_info.value)

    def test_complete_raises_conflict_error_when_already_completed(self):
        """이미 완료된 상태에서 complete()를 호출하면 ConflictError가 발생해야 한다"""
        # Given
        registration = Registration()
        registration.status = RegistrationStatus.COMPLETED  # 이미 완료된 상태

        # When & Then
        with pytest.raises(ConflictError) as exc_info:
            registration.complete()

        assert "완료 처리가 불가능한 상태입니다." in str(exc_info.value)

    def test_complete_success_when_paid_status(self):
        """PAID 상태에서 complete() 호출 시 성공해야 한다"""
        # Given
        registration = Registration()
        registration.status = RegistrationStatus.PAID
        registration.completed_at = None
        assert registration.is_completable is True

        # When
        registration.complete()

        # Then
        assert registration.completed_at is not None

    def test_complete_preserves_existing_completed_at_when_called_successfully(self):
        """PAID 상태에서 complete() 호출 시 completed_at이 설정되는지 확인"""
        # Given
        registration = Registration()
        registration.status = RegistrationStatus.PAID
        old_time = None
        registration.completed_at = old_time

        # When
        registration.complete()

        # Then
        assert registration.completed_at is not None
        assert registration.completed_at != old_time

    def test_paid_success_when_pending_status(self):
        """PENDING 상태에서 paid() 호출 시 성공해야 한다"""
        # Given
        registration = Registration()
        registration.status = RegistrationStatus.PENDING

        # When
        registration.paid()

        # Then
        assert registration.status == RegistrationStatus.PAID.value

    def test_paid_raises_conflict_error_when_already_paid(self):
        """이미 PAID 상태에서 paid()를 호출하면 ConflictError가 발생해야 한다"""
        # Given
        registration = Registration()
        registration.status = RegistrationStatus.PAID

        # When & Then
        with pytest.raises(ConflictError) as exc_info:
            registration.paid()

        assert "결제 완료 처리가 불가능한 상태입니다." in str(exc_info.value)

    def test_paid_raises_conflict_error_when_completed_status(self):
        """COMPLETED 상태에서 paid()를 호출하면 ConflictError가 발생해야 한다"""
        # Given
        registration = Registration()
        registration.status = RegistrationStatus.COMPLETED

        # When & Then
        with pytest.raises(ConflictError) as exc_info:
            registration.paid()

        assert "결제 완료 처리가 불가능한 상태입니다." in str(exc_info.value)

    def test_paid_changes_status_to_paid_enum_value(self):
        """paid() 메서드가 status를 올바른 enum 값으로 설정하는지 확인"""
        # Given
        registration = Registration()
        registration.status = RegistrationStatus.PENDING

        # When
        registration.paid()

        # Then
        assert registration.status == RegistrationStatus.PAID.value
