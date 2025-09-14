from fastapi import APIRouter, Depends
from starlette import status

from edu_register_api.core.depends import get_current_user, get_payment_service
from edu_register_api.schemas.auth import UserInfo
from edu_register_api.services.payment_service import PaymentService

router = APIRouter(tags=["Payment"])


@router.post(
    "/payments/{payment_id:int}/cancel",
    summary="결제 취소",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"description": "인증 실패"},
        404: {"description": "존재하지 않는 결제내역"},
        409: {"description": "비즈니스 에러"},
    },
)
def cancel_payment(
    payment_id: int,
    current_user: UserInfo = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service),
):
    payment_service.cancel(payment_id=payment_id, user_id=current_user.id)
