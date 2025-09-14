from edu_register_api.core.uow import UnitOfWork
from edu_register_api.enums import ItemType, ItemStatusFilter, ItemSortType
from edu_register_api.schemas.test import TestListResponse, TestResponse
from edu_register_api.schemas.common import PaginationResponse


class TestService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def get_test_list(
        self,
        user_id: int | None = None,
        page: int = 1,
        size: int = 10,
        status_filter: ItemStatusFilter = None,
        sort: ItemSortType = ItemSortType.CREATED,
    ) -> TestListResponse:
        tests, total = self.uow.item_repository.get_items_with_pagination(
            user_id=user_id,
            item_type=ItemType.TEST,
            page=page,
            size=size,
            status_filter=status_filter,
            sort=sort,
        )

        test_responses = []
        for test in tests:
            test_responses.append(TestResponse.from_query_result(test))

        return TestListResponse(
            tests=test_responses,
            pagination=PaginationResponse(
                page=page,
                size=size,
                total=total,
            ),
        )
