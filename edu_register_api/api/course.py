from fastapi import APIRouter, Depends, Query
from starlette import status

from edu_register_api.core.depends import (
    get_current_user,
    get_registration_service,
    get_course_service,
)
from edu_register_api.enums import ItemType, ItemStatusFilter, ItemSortType
from edu_register_api.schemas.auth import UserInfo
from edu_register_api.schemas.course import CourseListResponse
from edu_register_api.schemas.registration import PaymentInfo
from edu_register_api.services import CourseService
from edu_register_api.services.registration_service import RegistrationService

router = APIRouter(prefix="/courses", tags=["Course"])


@router.get(
    "",
    summary="수업 목록 조회",
    status_code=status.HTTP_200_OK,
    response_model=CourseListResponse,
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
    course_service: CourseService = Depends(get_course_service),
) -> CourseListResponse:
    return course_service.get_course_list(
        user_id=current_user.id,
        page=page,
        size=size,
        status_filter=status_filter,
        sort=sort,
    )


@router.post(
    "/{course_id:int}/enroll",
    summary="수업 수강 신청",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"description": "인증 실패"},
        404: {"description": "존재하지 않는 수업"},
        409: {"description": "비즈니스 에러"},
    },
)
def enroll_course(
    course_id: int,
    payment_info: PaymentInfo,
    current_user: UserInfo = Depends(get_current_user),
    registration_service: RegistrationService = Depends(get_registration_service),
):
    registration_service.register(
        user_id=current_user.id,
        item_id=course_id,
        payment_info=payment_info,
        item_type=ItemType.COURSE,
    )


@router.post(
    "/{course_id:int}/complete",
    summary="수업 수강 완료 처리",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"description": "인증 실패"},
        404: {"description": "존재하지 않는 수업"},
        409: {"description": "비즈니스 에러"},
    },
)
def complete_course(
    course_id: int,
    current_user: UserInfo = Depends(get_current_user),
    registration_service: RegistrationService = Depends(get_registration_service),
):
    registration_service.complete_registration(
        user_id=current_user.id, item_id=course_id, item_type=ItemType.COURSE
    )
