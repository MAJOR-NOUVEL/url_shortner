from pydantic import BaseModel


class ClicksPerDaySchema(BaseModel):
    date: str
    clicks: int

class BreakdownItemSchema(BaseModel):
    name: str
    count: int
    percentage: float

class AnalyticsResponseSchema(BaseModel):
    url_id: int
    short_code: str
    original_url: str
    total_clicks: int
    unique_visitors: int
    clicks_per_day: list[ClicksPerDaySchema]
    top_referrers: list[BreakdownItemSchema]
    devices: list[BreakdownItemSchema]
    browsers: list[BreakdownItemSchema]
    countries: list[BreakdownItemSchema]
