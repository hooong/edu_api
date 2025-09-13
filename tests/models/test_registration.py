from datetime import datetime, timezone
import pytest

from edu_register_api.core.erros import ConflictError
from edu_register_api.models.registration import Registration


class TestRegistration:
    def test_is_completed_when_completed_at_is_none(self):
        """completed_at이 None일 때 is_completed는 False를 반환해야 한다"""
        # Given
        registration = Registration()
        registration.completed_at = None

        # When
        result = registration.is_completed

        # Then
        assert result is False

    def test_is_completed_when_completed_at_is_set(self):
        """completed_at이 설정되어 있을 때 is_completed는 True를 반환해야 한다"""
        # Given
        registration = Registration()
        registration.completed_at = datetime.now(timezone.utc)

        # When
        result = registration.is_completed

        # Then
        assert result is True

    def test_complete_sets_completed_at_to_current_time(self):
        """complete() 메서드는 completed_at을 현재 시간으로 설정해야 한다"""
        # Given
        registration = Registration()
        registration.completed_at = None
        before_complete = datetime.now(timezone.utc)

        # When
        registration.complete()
        after_complete = datetime.now(timezone.utc)

        # Then
        assert registration.completed_at is not None
        assert before_complete <= registration.completed_at <= after_complete
        assert registration.completed_at.tzinfo == timezone.utc

    def test_complete_makes_is_completed_true(self):
        """complete() 메서드 호출 후 is_completed는 True가 되어야 한다"""
        # Given
        registration = Registration()
        registration.completed_at = None
        assert registration.is_completed is False

        # When
        registration.complete()

        # Then
        assert registration.is_completed is True

    def test_complete_raises_conflict_error_when_already_completed(self):
        """이미 완료된 상태에서 complete()를 호출하면 ConflictError가 발생해야 한다"""
        # Given
        registration = Registration()
        registration.completed_at = None
        registration.complete()  # 첫 번째 완료
        assert registration.is_completed is True

        # When & Then
        with pytest.raises(ConflictError) as exc_info:
            registration.complete()  # 두 번째 호출 시 에러 발생

        assert "이미 완료된 Item입니다." in str(exc_info.value)

    def test_complete_raises_conflict_error_when_completed_at_already_set(self):
        """completed_at이 이미 설정된 상태에서 complete()를 호출하면 ConflictError가 발생해야 한다"""
        # Given
        registration = Registration()
        registration.completed_at = datetime(2020, 1, 1, tzinfo=timezone.utc)
        assert registration.is_completed is True

        # When & Then
        with pytest.raises(ConflictError) as exc_info:
            registration.complete()

        assert "이미 완료된 Item입니다." in str(exc_info.value)
