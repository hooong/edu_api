from datetime import date

from edu_register_api.core.erros import NotFoundError, ConflictError, ValidationError
from edu_register_api.core.uow import UnitOfWork
from edu_register_api.enums import PaymentStatus, PaymentStatusFilter, PaymentMethod
from edu_register_api.models import Payment
from edu_register_api.schemas.payment import (
    PaymentListResponse,
    PaymentDetailResponse,
    PaginationResponse,
    PaymentItemInfo,
    PaymentRegistrationInfo,
)


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

    def get_user_payments(
        self,
        user_id: int,
        page: int = 1,
        size: int = 10,
        payment_status: PaymentStatusFilter = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> PaymentListResponse:
        if start_date and end_date and start_date > end_date:
            raise ValidationError("시작일은 종료일보다 미래일 수 없습니다.")

        payments, total = self.uow.payment_repository.get_user_payments_with_pagination(
            user_id=user_id,
            page=page,
            size=size,
            start_date=start_date,
            end_date=end_date,
            payment_status=payment_status,
        )

        payment_responses = []
        for payment in payments:
            payment_detail = PaymentDetailResponse(
                id=payment.id,
                amount=payment.amount,
                payment_status=PaymentStatus(payment.status),
                payment_method=PaymentMethod(payment.method),
                paid_at=payment.paid_at,
                cancelled_at=payment.cancelled_at,
                created_at=payment.created_at,
                item=PaymentItemInfo(
                    id=payment.registration.item.id,
                    title=payment.registration.item.title,
                    item_type=payment.registration.item.item_type,
                ),
                registration=PaymentRegistrationInfo(
                    id=payment.registration_id,
                    registration_status=payment.registration.status,
                    completed_at=payment.registration.completed_at,
                    deleted_at=payment.registration.deleted_at,
                ),
            )
            payment_responses.append(payment_detail)

        return PaymentListResponse(
            payments=payment_responses,
            pagination=PaginationResponse(
                page=page,
                size=size,
                total=total,
            ),
        )
