from edu_register_api.core.uow import UnitOfWork
from edu_register_api.enums import ItemType, ItemStatusFilter, ItemSortType
from edu_register_api.schemas.course import CourseListResponse, CourseResponse
from edu_register_api.schemas.common import PaginationResponse


class CourseService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def get_course_list(
        self,
        user_id: int | None = None,
        page: int = 1,
        size: int = 10,
        status_filter: ItemStatusFilter = None,
        sort: ItemSortType = ItemSortType.CREATED,
    ) -> CourseListResponse:
        courses, total = self.uow.item_repository.get_items_with_pagination(
            user_id=user_id,
            item_type=ItemType.COURSE,
            page=page,
            size=size,
            status_filter=status_filter,
            sort=sort,
        )

        course_responses = []
        for course in courses:
            course_responses.append(CourseResponse.from_query_result(course))

        return CourseListResponse(
            courses=course_responses,
            pagination=PaginationResponse(
                page=page,
                size=size,
                total=total,
            ),
        )
