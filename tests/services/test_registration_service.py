import pytest
from unittest.mock import Mock

from edu_register_api.core.erros import NotFoundError, ConflictError
from edu_register_api.enums import ItemType
from edu_register_api.models.registration import Registration
from edu_register_api.services.registration_service import RegistrationService


class TestRegistrationService:
    @pytest.fixture
    def mock_uow(self):
        uow = Mock()
        uow.registration_repository = Mock()
        return uow

    @pytest.fixture
    def registration_service(self, mock_uow):
        return RegistrationService(mock_uow)

    @pytest.fixture
    def mock_registration(self):
        registration = Mock(spec=Registration)
        registration.item = Mock()
        registration.item.item_type = ItemType.TEST
        registration.complete = Mock()
        return registration

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
