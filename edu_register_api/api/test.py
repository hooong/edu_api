from fastapi import APIRouter, Depends, Query
from starlette import status

from edu_register_api.core.depends import (
    get_current_user,
    get_registration_service,
    get_test_service,
)
from edu_register_api.enums import ItemType, ItemStatusFilter, ItemSortType
from edu_register_api.schemas.auth import UserInfo
from edu_register_api.schemas.registration import PaymentInfo
from edu_register_api.schemas.test import TestListResponse
from edu_register_api.services import RegistrationService
from edu_register_api.services import TestService

router = APIRouter(prefix="/tests", tags=["Test"])


@router.get(
    "",
    summary="시험 목록 조회",
    status_code=status.HTTP_200_OK,
    response_model=TestListResponse,
    responses={
        401: {"description": "인증 실패"},
    },
)
def get_tests(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    status_filter: ItemStatusFilter | None = Query(default=None, alias="status"),
    sort: ItemSortType = Query(default=ItemSortType.CREATED),
    current_user: UserInfo = Depends(get_current_user),
    test_service: TestService = Depends(get_test_service),
) -> TestListResponse:
    return test_service.get_test_list(
        user_id=current_user.id,
        page=page,
        size=size,
        status_filter=status_filter,
        sort=sort,
    )


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
