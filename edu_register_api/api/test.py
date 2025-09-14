from fastapi import APIRouter, Depends
from starlette import status

from edu_register_api.core.depends import get_current_user, get_registration_service
from edu_register_api.enums import ItemType
from edu_register_api.schemas.auth import UserInfo
from edu_register_api.schemas.registration import PaymentInfo
from edu_register_api.services.registration_service import RegistrationService

router = APIRouter(prefix="/tests", tags=["Test"])


@router.post(
    "/{test_id:int}/apply",
    summary="시험 응시 신청",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"description": "인증 실패"},
        404: {"description": "존재하지 않는 시험"},
        409: {"description": "비즈니스 에러"},
    },
)
def apply_test(
    test_id: int,
    payment_info: PaymentInfo,
    current_user: UserInfo = Depends(get_current_user),
    registration_service: RegistrationService = Depends(get_registration_service),
):
    registration_service.register(
        user_id=current_user.id,
        item_id=test_id,
        payment_info=payment_info,
        item_type=ItemType.TEST,
    )


@router.post(
    "/{test_id:int}/complete",
    summary="시험 응시 완료 처리",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"description": "인증 실패"},
        404: {"description": "존재하지 않는 수업"},
        409: {"description": "비즈니스 에러"},
    },
)
def complete_test(
    test_id: int,
    current_user: UserInfo = Depends(get_current_user),
    registration_service: RegistrationService = Depends(get_registration_service),
):
    registration_service.complete_registration(
        user_id=current_user.id, item_id=test_id, item_type=ItemType.TEST
    )
