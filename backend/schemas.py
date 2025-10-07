from pydantic import BaseModel, HttpUrl

class CreateRequest(BaseModel):
    url: HttpUrl

class CreateResponse(BaseModel):
    short_url: str

class AnalyticsResponse(BaseModel):
    original_url: str
    clicks: int
    created_at: str
