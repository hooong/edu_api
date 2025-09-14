from datetime import date

from fastapi import APIRouter, Depends
from fastapi.params import Query
from starlette import status

from edu_register_api.core.depends import get_current_user, get_payment_service
from edu_register_api.enums import PaymentStatusFilter
from edu_register_api.schemas.auth import UserInfo
from edu_register_api.schemas.payment import PaymentListResponse
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


@router.get(
    "/me/payments",
    summary="결제 내역 조회(본인)",
    status_code=status.HTTP_200_OK,
    response_model=PaymentListResponse,
    responses={
        400: {"description": "요청값 검증 실패"},
        401: {"description": "인증 실패"},
    },
)
def get_my_payments(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    payment_status: PaymentStatusFilter | None = Query(
        default=None, alias="status", description="결제 상태 필터"
    ),
    start_date: date | None = Query(
        default=None, alias="from", description="조회 시작 날짜 (결제 완료 시점 기준)"
    ),
    end_date: date | None = Query(
        default=None, alias="to", description="조회 종료 날짜 (결제 완료 시점 기준)"
    ),
    current_user: UserInfo = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service),
) -> PaymentListResponse:
    return payment_service.get_user_payments(
        user_id=current_user.id,
        page=page,
        size=size,
        payment_status=payment_status,
        start_date=start_date,
        end_date=end_date,
    )
