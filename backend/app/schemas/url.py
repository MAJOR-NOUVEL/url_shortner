import re
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.utils.security import validate_url_security

RESERVED_SLUGS = {
    "api", "static", "docs", "redoc", "openapi", "health",
    "favicon.ico", "robots.txt", "admin", "dashboard", "auth", "urls"
}

class CreateURLSchema(BaseModel):
    url: str = Field(..., description="Destination URL to shorten (HTTP or HTTPS)")
    custom_alias: str | None = Field(None, min_length=3, max_length=32, description="Optional custom vanity alias")
    expires_at: datetime | None = Field(None, description="Optional ISO timestamp when link expires")
    expires_in_hours: int | None = Field(None, ge=1, le=8760, description="Optional relative expiration in hours")

    @field_validator("url")
    def validate_url(cls, v: str) -> str:
        v = v.strip()
        if not v.startswith(("http://", "https://")):
            v = f"https://{v}"

        is_safe, error_msg = validate_url_security(v)
        if not is_safe:
            raise ValueError(error_msg)
        return v

    @field_validator("custom_alias")
    def validate_alias(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        if not v:
            return None
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Custom alias may only contain letters, numbers, hyphens, and underscores.")
        if v.lower() in RESERVED_SLUGS:
            raise ValueError(f"'{v}' is a reserved system keyword and cannot be used as an alias.")
        return v

class URLResponseSchema(BaseModel):
    id: int
    short_code: str
    short_url: str
    original_url: str
    custom_alias: bool
    user_id: int | None = None
    is_active: bool
    is_expired: bool
    created_at: str | None = None
    expires_at: str | None = None
    click_count: int = 0
