import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch

from edu_register_api.core.erros import NotFoundError, ConflictError
from edu_register_api.enums import ItemType, PaymentMethod
from edu_register_api.models.registration import Registration
from edu_register_api.models.item import Item
from edu_register_api.schemas.registration import PaymentInfo
from edu_register_api.services.registration_service import RegistrationService


class TestRegistrationService:
    @pytest.fixture
    def mock_uow(self):
        uow = Mock()
        uow.registration_repository = Mock()
        uow.item_repository = Mock()
        uow.payment_repository = Mock()
        uow.commit = Mock()
        uow.rollback = Mock()
        return uow

    @pytest.fixture
    def mock_redis_client(self):
        redis_client = Mock()
        redis_client.lock = Mock()
        return redis_client

    @pytest.fixture
    def registration_service(self, mock_uow, mock_redis_client):
        return RegistrationService(mock_uow, mock_redis_client)

    @pytest.fixture
    def mock_registration(self):
        registration = Mock(spec=Registration)
        registration.item = Mock()
        registration.item.item_type = ItemType.TEST
        registration.complete = Mock()
        return registration

    @pytest.fixture
    def mock_item(self):
        item = Mock(spec=Item)
        item.id = 100
        item.item_type = ItemType.TEST
        now = datetime.now(timezone.utc)
        item.start_at = now - timedelta(days=1)
        item.end_at = now + timedelta(days=30)
        return item

    @pytest.fixture
    def mock_item_not_available(self):
        item = Mock(spec=Item)
        item.id = 200
        item.item_type = ItemType.TEST
        now = datetime.now(timezone.utc)
        item.start_at = now - timedelta(days=30)  # 30일 전 시작
        item.end_at = now - timedelta(days=1)  # 1일 전 종료 (이미 종료됨)
        return item

    @pytest.fixture
    def payment_info(self):
        return PaymentInfo(amount=50000, payment_method=PaymentMethod.CARD)

    def test_complete_registration_success(
        self, registration_service, mock_uow, mock_registration
    ):
        """정상적인 등록 완료 처리"""
        # Given
        user_id = 1
        item_id = 100
        item_type = ItemType.TEST
        mock_uow.registration_repository.get_by_item_id_and_user_id.return_value = (
            mock_registration
        )

        # When
        registration_service.complete_registration(user_id, item_id, item_type)

        # Then
        mock_uow.registration_repository.get_by_item_id_and_user_id.assert_called_once_with(
            item_id=item_id, user_id=user_id
        )
        mock_registration.complete.assert_called_once()

    def test_complete_registration_not_found(self, registration_service, mock_uow):
        """등록 내역을 찾을 수 없는 경우"""
        # Given
        user_id = 1
        item_id = 100
        item_type = ItemType.TEST
        mock_uow.registration_repository.get_by_item_id_and_user_id.return_value = None

        # When & Then
        with pytest.raises(NotFoundError) as exc_info:
            registration_service.complete_registration(user_id, item_id, item_type)

        assert "완료처리 할 내역을 찾을 수 없습니다." in str(exc_info.value)
        mock_uow.registration_repository.get_by_item_id_and_user_id.assert_called_once_with(
            item_id=item_id, user_id=user_id
        )

    def test_complete_registration_wrong_item_type(
        self, registration_service, mock_uow, mock_registration
    ):
        """잘못된 아이템 타입으로 요청한 경우"""
        # Given
        user_id = 1
        item_id = 100
        item_type = ItemType.COURSE  # 등록된 item은 TEST인데 COURSE로 요청
        mock_registration.item.item_type = ItemType.TEST
        mock_uow.registration_repository.get_by_item_id_and_user_id.return_value = (
            mock_registration
        )

        # When & Then
        with pytest.raises(ConflictError) as exc_info:
            registration_service.complete_registration(user_id, item_id, item_type)

        assert "잘못된 타입의 Item에 대한 요청입니다." in str(exc_info.value)
        mock_uow.registration_repository.get_by_item_id_and_user_id.assert_called_once_with(
            item_id=item_id, user_id=user_id
        )
        mock_registration.complete.assert_not_called()

    def test_complete_registration_not_completable(
        self, registration_service, mock_uow, mock_registration
    ):
        """완료 불가능한 상태의 등록을 완료 처리하려는 경우"""
        # Given
        user_id = 1
        item_id = 100
        item_type = ItemType.TEST
        mock_registration.complete.side_effect = ConflictError(
            "완료 처리가 불가능한 상태입니다."
        )
        mock_uow.registration_repository.get_by_item_id_and_user_id.return_value = (
            mock_registration
        )

        # When & Then
        with pytest.raises(ConflictError) as exc_info:
            registration_service.complete_registration(user_id, item_id, item_type)

        assert "완료 처리가 불가능한 상태입니다." in str(exc_info.value)
        mock_uow.registration_repository.get_by_item_id_and_user_id.assert_called_once_with(
            item_id=item_id, user_id=user_id
        )
        mock_registration.complete.assert_called_once()

    def test_complete_registration_with_course_type(
        self, registration_service, mock_uow, mock_registration
    ):
        """COURSE 타입 아이템 완료 처리"""
        # Given
        user_id = 1
        item_id = 200
        item_type = ItemType.COURSE
        mock_registration.item.item_type = ItemType.COURSE
        mock_uow.registration_repository.get_by_item_id_and_user_id.return_value = (
            mock_registration
        )

        # When
        registration_service.complete_registration(user_id, item_id, item_type)

        # Then
        mock_uow.registration_repository.get_by_item_id_and_user_id.assert_called_once_with(
            item_id=item_id, user_id=user_id
        )
        mock_registration.complete.assert_called_once()

    def test_register_success_with_payment(
        self, registration_service, mock_uow, mock_redis_client, mock_item, payment_info
    ):
        """결제 성공 시 정상적인 등록 처리"""
        # Given
        user_id = 1
        item_id = 100
        item_type = ItemType.TEST

        mock_uow.item_repository.get_by_id_and_item_type.return_value = mock_item
        mock_uow.registration_repository.get_by_item_id_and_user_id.return_value = None

        mock_redis_client.lock.return_value.__enter__ = Mock(return_value=True)
        mock_redis_client.lock.return_value.__exit__ = Mock(return_value=None)

        mock_new_registration = Mock(spec=Registration)
        mock_new_registration.id = 1
        mock_new_registration.paid = Mock()
        mock_uow.registration_repository.save.return_value = mock_new_registration

        with patch.object(registration_service, "_process_payment", return_value=True):
            # When
            registration_service.register(user_id, item_id, item_type, payment_info)

        # Then
        mock_uow.item_repository.get_by_id_and_item_type.assert_called_once_with(
            id=item_id, item_type=item_type
        )
        mock_uow.registration_repository.get_by_item_id_and_user_id.assert_called_once_with(
            item_id=item_id, user_id=user_id
        )
        mock_redis_client.lock.assert_called_once_with(
            f"registration:{user_id}:{item_id}"
        )
        mock_uow.registration_repository.save.assert_called()
        mock_uow.payment_repository.save.assert_called()
        mock_new_registration.paid.assert_called_once()

    def test_register_payment_failure(
        self, registration_service, mock_uow, mock_redis_client, mock_item, payment_info
    ):
        """결제 실패 시 등록 롤백"""
        # Given
        user_id = 1
        item_id = 100
        item_type = ItemType.TEST

        mock_uow.item_repository.get_by_id_and_item_type.return_value = mock_item
        mock_uow.registration_repository.get_by_item_id_and_user_id.return_value = None

        mock_redis_client.lock.return_value.__enter__ = Mock(return_value=True)
        mock_redis_client.lock.return_value.__exit__ = Mock(return_value=None)

        mock_new_registration = Mock(spec=Registration)
        mock_new_registration.id = 1
        mock_uow.registration_repository.save.return_value = mock_new_registration

        with patch.object(registration_service, "_process_payment", return_value=False):
            # When & Then
            with pytest.raises(ConflictError) as exc_info:
                registration_service.register(user_id, item_id, item_type, payment_info)

            assert "결제에 실패하였습니다. 재시도 부탁드립니다." in str(exc_info.value)

        # Then
        mock_uow.registration_repository.hard_delete.assert_called_once_with(
            mock_new_registration.id
        )

    def test_register_item_not_found(
        self, registration_service, mock_uow, mock_redis_client, payment_info
    ):
        """존재하지 않는 아이템에 대한 등록 시도"""
        # Given
        user_id = 1
        item_id = 999
        item_type = ItemType.TEST

        mock_uow.item_repository.get_by_id_and_item_type.return_value = None

        # When & Then
        with pytest.raises(NotFoundError) as exc_info:
            registration_service.register(user_id, item_id, item_type, payment_info)

        assert "존재하지 않는 Item입니다." in str(exc_info.value)
        mock_uow.item_repository.get_by_id_and_item_type.assert_called_once_with(
            id=item_id, item_type=item_type
        )

    def test_register_already_registered(
        self,
        registration_service,
        mock_uow,
        mock_redis_client,
        mock_item,
        mock_registration,
        payment_info,
    ):
        """이미 등록된 아이템에 대한 중복 등록 시도"""
        # Given
        user_id = 1
        item_id = 100
        item_type = ItemType.TEST

        mock_uow.item_repository.get_by_id_and_item_type.return_value = mock_item
        mock_uow.registration_repository.get_by_item_id_and_user_id.return_value = (
            mock_registration
        )

        # When & Then
        with pytest.raises(ConflictError) as exc_info:
            registration_service.register(user_id, item_id, item_type, payment_info)

        assert "이미 등록한 Item이 존재합니다." in str(exc_info.value)
        mock_uow.registration_repository.get_by_item_id_and_user_id.assert_called_once_with(
            item_id=item_id, user_id=user_id
        )

    def test_register_redis_lock_usage(
        self, registration_service, mock_uow, mock_redis_client, mock_item, payment_info
    ):
        """Redis 분산 락이 올바르게 사용되는지 확인"""
        # Given
        user_id = 1
        item_id = 100
        item_type = ItemType.TEST

        mock_uow.item_repository.get_by_id_and_item_type.return_value = mock_item
        mock_uow.registration_repository.get_by_item_id_and_user_id.return_value = None

        mock_redis_client.lock.return_value.__enter__ = Mock(return_value=True)
        mock_redis_client.lock.return_value.__exit__ = Mock(return_value=None)

        mock_new_registration = Mock(spec=Registration)
        mock_new_registration.id = 1
        mock_new_registration.paid = Mock()
        mock_uow.registration_repository.save.return_value = mock_new_registration

        with patch.object(registration_service, "_process_payment", return_value=True):
            # When
            registration_service.register(user_id, item_id, item_type, payment_info)

        # Then
        expected_lock_key = f"registration:{user_id}:{item_id}"
        mock_redis_client.lock.assert_called_once_with(expected_lock_key)

    def test_register_invalid_time_period(
        self, registration_service, mock_uow, mock_item_not_available, payment_info
    ):
        """신청 불가능한 기간의 아이템에 대한 등록 시도"""
        # Given
        user_id = 1
        item_id = 200
        item_type = ItemType.TEST

        mock_uow.item_repository.get_by_id_and_item_type.return_value = (
            mock_item_not_available
        )
        mock_uow.registration_repository.get_by_item_id_and_user_id.return_value = None

        # When & Then
        with pytest.raises(ConflictError) as exc_info:
            registration_service.register(user_id, item_id, item_type, payment_info)

        assert "신청 가능 기간이 아닙니다." in str(exc_info.value)
        mock_uow.item_repository.get_by_id_and_item_type.assert_called_once_with(
            id=item_id, item_type=item_type
        )
