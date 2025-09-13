from edu_register_api.core.erros import NotFoundError, ConflictError
from edu_register_api.core.uow import UnitOfWork
from edu_register_api.enums import ItemType
from edu_register_api.models import Registration


class RegistrationService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def complete_registration(
        self, user_id: int, item_id: int, item_type: ItemType
    ) -> None:
        registration: Registration = (
            self.uow.registration_repository.get_by_item_id_and_user_id(
                item_id=item_id, user_id=user_id
            )
        )

        if registration is None:
            raise NotFoundError("완료처리 할 내역을 찾을 수 없습니다.")

        if registration.item.item_type != item_type:
            raise ConflictError("잘못된 타입의 Item에 대한 요청입니다.")

        registration.complete()
