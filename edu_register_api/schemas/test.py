from datetime import datetime
from typing import List, Self

from pydantic import BaseModel

from edu_register_api.enums import ItemType
from edu_register_api.models import Item
from edu_register_api.schemas.common import PaginationResponse


class TestResponse(BaseModel):
    id: int
    title: str
    item_type: ItemType
    start_at: datetime
    end_at: datetime
    created_at: datetime
    is_registered: bool
    registration_count: int

    @classmethod
    def from_query_result(cls, item: Item) -> Self:
        if not (hasattr(item, "is_registered") and hasattr(item, "registration_count")):
            raise AttributeError(
                "Item for TestResponse must have is_registered and registration_count"
            )

        return cls(
            id=item.id,
            title=item.title,
            item_type=ItemType(item.item_type),
            start_at=item.start_at,
            end_at=item.end_at,
            created_at=item.created_at,
            is_registered=getattr(item, "is_registered", False),
            registration_count=getattr(item, "registration_count", 0),
        )


class TestListResponse(BaseModel):
    tests: List[TestResponse]
    pagination: PaginationResponse
