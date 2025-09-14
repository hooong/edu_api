import pytest
from unittest.mock import Mock, patch

from edu_register_api.core.erros import NotFoundError, ConflictError
from edu_register_api.models.payment import Payment
from edu_register_api.models.registration import Registration
from edu_register_api.services.payment_service import PaymentService


class TestPaymentService:
    @pytest.fixture
    def mock_uow(self):
        uow = Mock()
        uow.payment_repository = Mock()
        uow.registration_repository = Mock()
        return uow

    @pytest.fixture
    def payment_service(self, mock_uow):
        return PaymentService(mock_uow)

    @pytest.fixture
    def mock_registration(self):
        registration = Mock(spec=Registration)
        registration.id = 1
        registration.user_id = 123
        registration.is_completed = False
        return registration

    @pytest.fixture
    def mock_payment(self, mock_registration):
        payment = Mock(spec=Payment)
        payment.id = 1
        payment.registration_id = 1
        payment.registration = mock_registration
        payment.cancel = Mock()
        return payment

    def test_cancel_success(self, payment_service, mock_uow, mock_payment):
        """정상적인 결제 취소 처리"""
        # Given
        payment_id = 1
        user_id = 123
        mock_uow.payment_repository.get_by_id_with_registration.return_value = (
            mock_payment
        )

        with patch.object(payment_service, "_payment_cancel", return_value=True):
            # When
            payment_service.cancel(payment_id, user_id)

        # Then
        mock_uow.payment_repository.get_by_id_with_registration.assert_called_once_with(
            id=payment_id
        )
        mock_payment.cancel.assert_called_once()
        mock_uow.registration_repository.delete.assert_called_once_with(
            mock_payment.registration_id
        )

    def test_cancel_payment_not_found(self, payment_service, mock_uow):
        """존재하지 않는 결제 내역에 대한 취소 시도"""
        # Given
        payment_id = 999
        user_id = 123
        mock_uow.payment_repository.get_by_id_with_registration.return_value = None

        # When & Then
        with pytest.raises(NotFoundError) as exc_info:
            payment_service.cancel(payment_id, user_id)

        assert "존재하지 않는 결제 내역입니다." in str(exc_info.value)
        mock_uow.payment_repository.get_by_id_with_registration.assert_called_once_with(
            id=payment_id
        )

    def test_cancel_unauthorized_user(self, payment_service, mock_uow, mock_payment):
        """다른 사용자의 결제 내역 취소 시도"""
        # Given
        payment_id = 1
        user_id = 456  # 다른 사용자 ID
        mock_payment.registration.user_id = 123  # 실제 소유자 ID
        mock_uow.payment_repository.get_by_id_with_registration.return_value = (
            mock_payment
        )

        # When & Then
        with pytest.raises(ConnectionError) as exc_info:
            payment_service.cancel(payment_id, user_id)

        assert "본인의 결제 내역만 취소가 가능합니다." in str(exc_info.value)
        mock_uow.payment_repository.get_by_id_with_registration.assert_called_once_with(
            id=payment_id
        )

    def test_cancel_already_completed_registration(
        self, payment_service, mock_uow, mock_payment
    ):
        """이미 완료된 등록에 대한 결제 취소 시도"""
        # Given
        payment_id = 1
        user_id = 123
        mock_payment.registration.is_completed = True
        mock_uow.payment_repository.get_by_id_with_registration.return_value = (
            mock_payment
        )

        # When & Then
        with pytest.raises(ConflictError) as exc_info:
            payment_service.cancel(payment_id, user_id)

        assert "이미 완료된 내역은 취소가 불가능합니다." in str(exc_info.value)
        mock_uow.payment_repository.get_by_id_with_registration.assert_called_once_with(
            id=payment_id
        )

    def test_cancel_payment_cancel_failure(
        self, payment_service, mock_uow, mock_payment
    ):
        """외부 결제 시스템에서 취소 실패"""
        # Given
        payment_id = 1
        user_id = 123
        mock_uow.payment_repository.get_by_id_with_registration.return_value = (
            mock_payment
        )

        with patch.object(payment_service, "_payment_cancel", return_value=False):
            # When & Then
            with pytest.raises(ConflictError) as exc_info:
                payment_service.cancel(payment_id, user_id)

            assert "결제 취소에 실패하였습니다." in str(exc_info.value)

        # Then
        mock_uow.payment_repository.get_by_id_with_registration.assert_called_once_with(
            id=payment_id
        )
        # 취소 실패 시에는 payment.cancel()과 registration 삭제가 호출되지 않아야 함
        mock_payment.cancel.assert_not_called()
        mock_uow.registration_repository.delete.assert_not_called()
