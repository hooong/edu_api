from datetime import datetime, timezone

from edu_register_api.core.erros import NotFoundError, ConflictError
from edu_register_api.core.redis import RedisClient
from edu_register_api.core.uow import UnitOfWork
from edu_register_api.enums import ItemType, RegistrationStatus, PaymentStatus
from edu_register_api.models import Registration, Payment, Item
from edu_register_api.schemas.registration import PaymentInfo


class RegistrationService:
    def __init__(self, uow: UnitOfWork, redis_client: RedisClient):
        self.uow = uow
        self.redis_client = redis_client

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

    def register(
        self, user_id: int, item_id: int, item_type: ItemType, payment_info: PaymentInfo
    ) -> None:
        item: Item = self.uow.item_repository.get_by_id_and_item_type(
            id=item_id, item_type=item_type
        )
        if not item:
            raise NotFoundError("존재하지 않는 Item입니다.")

        registration: Registration = (
            self.uow.registration_repository.get_by_item_id_and_user_id(
                item_id=item_id, user_id=user_id
            )
        )

        if registration:
            raise ConflictError("이미 등록한 Item이 존재합니다.")

        now = datetime.now(timezone.utc)
        if (
            item.start_at.replace(tzinfo=timezone.utc) > now
            or item.end_at.replace(tzinfo=timezone.utc) < now
        ):
            raise ConflictError("신청 가능 기간이 아닙니다.")

        lock_key: str = f"registration:{user_id}:{item_id}"
        with self.redis_client.lock(lock_key):
            registration = Registration(
                user_id=user_id,
                item_id=item_id,
                status=RegistrationStatus.PENDING.value,
            )
            registration = self.uow.registration_repository.save(registration)

            is_paid: bool = self._process_payment()
            if is_paid:
                payment = Payment(
                    registration_id=registration.id,
                    amount=payment_info.amount,
                    method=payment_info.payment_method,
                    status=PaymentStatus.PAID.value,
                    paid_at=datetime.now(timezone.utc),
                )
                self.uow.payment_repository.save(payment)

                registration.paid()
            else:
                self.uow.registration_repository.hard_delete(registration.id)
                raise ConflictError("결제에 실패하였습니다. 재시도 부탁드립니다.")

    def _process_payment(self) -> bool:
        return True
