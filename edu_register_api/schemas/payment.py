from datetime import datetime
from typing import List

from pydantic import BaseModel

from edu_register_api.enums import PaymentStatus, PaymentMethod, RegistrationStatus
from edu_register_api.schemas.common import PaginationResponse


class PaymentItemInfo(BaseModel):
    id: int
    title: str
    item_type: str


class PaymentRegistrationInfo(BaseModel):
    id: int
    registration_status: RegistrationStatus
    completed_at: datetime | None
    deleted_at: datetime | None


class PaymentDetailResponse(BaseModel):
    id: int
    amount: float
    payment_status: PaymentStatus
    payment_method: PaymentMethod
    paid_at: datetime | None
    cancelled_at: datetime | None
    created_at: datetime
    item: PaymentItemInfo
    registration: PaymentRegistrationInfo


class PaymentListResponse(BaseModel):
    payments: List[PaymentDetailResponse]
    pagination: PaginationResponse
