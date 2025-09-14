from edu_register_api.core.erros import NotFoundError, ConflictError
from edu_register_api.core.uow import UnitOfWork
from edu_register_api.models import Payment


class PaymentService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def cancel(
        self,
        payment_id: int,
        user_id: int,
    ) -> None:
        payment: Payment = self.uow.payment_repository.get_by_id_with_registration(
            id=payment_id
        )

        if not payment:
            raise NotFoundError("존재하지 않는 결제 내역입니다.")

        if payment.registration.user_id != user_id:
            raise ConnectionError("본인의 결제 내역만 취소가 가능합니다.")

        if payment.registration.is_completed:
            raise ConflictError("이미 완료된 내역은 취소가 불가능합니다.")

        is_canceled = self._payment_cancel()
        if is_canceled:
            payment.cancel()
            self.uow.registration_repository.delete(payment.registration_id)
        else:
            raise ConflictError("결제 취소에 실패하였습니다.")

    def _payment_cancel(self) -> bool:
        return True
