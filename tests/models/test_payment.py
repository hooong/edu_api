from datetime import datetime, timezone
import pytest

from edu_register_api.core.erros import ConflictError
from edu_register_api.enums import PaymentStatus
from edu_register_api.models.payment import Payment


class TestPayment:
    def test_cancel_sets_status_to_canceled(self):
        """cancel() 메서드가 status를 CANCELED로 설정해야 한다"""
        # Given
        payment = Payment()
        payment.status = PaymentStatus.PAID.value
        payment.cancelled_at = None

        # When
        payment.cancel()

        # Then
        assert payment.status == PaymentStatus.CANCELED.value

    def test_cancel_sets_cancelled_at_to_current_time(self):
        """cancel() 메서드가 cancelled_at을 현재 시간으로 설정해야 한다"""
        # Given
        payment = Payment()
        payment.status = PaymentStatus.PAID.value
        payment.cancelled_at = None
        before_cancel = datetime.now(timezone.utc)

        # When
        payment.cancel()
        after_cancel = datetime.now(timezone.utc)

        # Then
        assert payment.cancelled_at is not None
        assert before_cancel <= payment.cancelled_at <= after_cancel
        assert payment.cancelled_at.tzinfo == timezone.utc

    def test_cancel_raises_error_when_status_is_pending(self):
        """PENDING 상태일 때 cancel() 메서드가 ConflictError를 발생시켜야 한다"""
        # Given
        payment = Payment()
        payment.status = PaymentStatus.PENDING.value
        payment.cancelled_at = None

        # When & Then
        with pytest.raises(ConflictError) as exc_info:
            payment.cancel()

        assert str(exc_info.value) == "409: 결제 취소가 불가능한 상태입니다."
        assert payment.status == PaymentStatus.PENDING.value
        assert payment.cancelled_at is None

    def test_cancel_raises_error_when_status_is_already_canceled(self):
        """이미 CANCELED 상태일 때 cancel() 메서드가 ConflictError를 발생시켜야 한다"""
        # Given
        payment = Payment()
        payment.status = PaymentStatus.CANCELED.value
        old_cancelled_time = datetime(2023, 1, 1, tzinfo=timezone.utc)
        payment.cancelled_at = old_cancelled_time

        # When & Then
        with pytest.raises(ConflictError) as exc_info:
            payment.cancel()

        assert str(exc_info.value) == "409: 결제 취소가 불가능한 상태입니다."
        assert payment.status == PaymentStatus.CANCELED.value
        assert payment.cancelled_at == old_cancelled_time

    def test_cancel_succeeds_when_status_is_failed(self):
        """FAILED 상태일 때 cancel() 메서드가 ConflictError를 발생시켜야 한다"""
        # Given
        payment = Payment()
        payment.status = PaymentStatus.FAILED.value
        payment.cancelled_at = None

        # When & Then
        with pytest.raises(ConflictError) as exc_info:
            payment.cancel()

        assert str(exc_info.value) == "409: 결제 취소가 불가능한 상태입니다."
        assert payment.status == PaymentStatus.FAILED.value
        assert payment.cancelled_at is None
