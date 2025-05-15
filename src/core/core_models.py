from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class RedisChallange(BaseModel):
    code: str
    code_challange: str = Field(min_length=43, max_length=128)
    method: Literal["S256", "plain"]


class AppTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    app_token: str
    token_type: Literal["Bearer"]
    expires_in: int = 3600
