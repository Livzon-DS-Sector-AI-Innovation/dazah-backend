"""Feishu tenant access token management with multi-bot support."""

import time

import httpx

from app.core.config import get_settings

_settings = get_settings()


class FeishuAuth:
    """Per-(app_id, app_secret) tenant access token cache.

    Default class-level access (`FeishuAuth.get_tenant_access_token()`) uses the
    primary bot from settings (FEISHU_APP_ID / FEISHU_APP_SECRET), preserving
    backward compatibility.

    Instance access lets a caller pick a specific bot:

        auth = FeishuAuth.vehicle()
        token = await auth.get_token()
    """

    # cache keyed by app_id -> (token, expire_at)
    _cache: dict[str, tuple[str, float]] = {}

    # legacy class-level fields retained for any caller that imports them
    _token: str | None = None
    _expire_at: float = 0.0

    def __init__(self, app_id: str, app_secret: str) -> None:
        self.app_id = app_id
        self.app_secret = app_secret

    # ----- factories -----

    @classmethod
    def default(cls) -> "FeishuAuth":
        return cls(_settings.FEISHU_APP_ID, _settings.FEISHU_APP_SECRET)

    @classmethod
    def vehicle(cls) -> "FeishuAuth":
        return cls(
            _settings.FEISHU_VEHICLE_APP_ID,
            _settings.FEISHU_VEHICLE_APP_SECRET,
        )

    @classmethod
    def training(cls) -> "FeishuAuth":
        return cls(
            _settings.FEISHU_TRAINING_APP_ID,
            _settings.FEISHU_TRAINING_APP_SECRET,
        )

    # ----- token fetch -----

    async def get_token(self) -> str:
        if not self.app_id or not self.app_secret:
            raise RuntimeError("Feishu app_id or app_secret not configured")

        cached = self._cache.get(self.app_id)
        now = time.time()
        if cached and now < cached[1] - 60:
            return cached[0]

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
                json={"app_id": self.app_id, "app_secret": self.app_secret},
                timeout=10.0,
            )
            resp.raise_for_status()
            data = resp.json()

        if data.get("code") != 0:
            raise RuntimeError(f"Feishu auth failed: {data}")

        token = data["tenant_access_token"]
        expire_at = now + data.get("expire", 7200)
        self._cache[self.app_id] = (token, expire_at)
        return token

    # backward-compat: existing callers do `FeishuAuth.get_tenant_access_token()`
    @classmethod
    async def get_tenant_access_token(cls) -> str:
        return await cls.default().get_token()
