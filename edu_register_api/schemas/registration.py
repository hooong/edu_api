from pydantic import BaseModel

from edu_register_api.enums import PaymentMethod


class PaymentInfo(BaseModel):
    amount: int
    payment_method: PaymentMethod
