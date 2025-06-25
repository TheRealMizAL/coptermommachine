from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field
from oidc_models import AnyHttpsUrl


class RedisChallange(BaseModel):
    code: str
    code_challange: str = Field(min_length=43, max_length=128)
    method: Literal["S256", "plain"]
    req_scope: str
    redirect_uri: AnyHttpsUrl


class AppTokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    app_token: str | None = None
    token_type: Literal["Bearer"] = "Bearer"
    expires_in: int = 3600
