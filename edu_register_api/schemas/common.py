from pydantic import BaseModel


class PaginationResponse(BaseModel):
    page: int
    size: int
    total: int
