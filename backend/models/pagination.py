from pydantic import BaseModel, Field


class Pagination(BaseModel):
    """
    Pagination model for API responses.
    """

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    genres: list[str]
    maximum_certification: str | None = Field(default=None, description="Maximum certification level for filtering movies")

class PaginatedResponse(BaseModel):
    """
    Base model for paginated API responses.
    """
    total: int
    page: int
    page_size: int
    total_pages: int
    items: list
