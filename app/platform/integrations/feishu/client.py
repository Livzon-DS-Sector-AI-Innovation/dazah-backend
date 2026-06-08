"""Feishu HTTP client with auth and retry."""

import httpx

from app.platform.integrations.base import IntegrationClient
from app.platform.integrations.feishu.auth import FeishuAuth


class FeishuClient(IntegrationClient):
    system_name = "feishu"
    base_url = "https://open.feishu.cn/open-apis"

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
                timeout=httpx.Timeout(15.0, connect=5.0),
            )
        return self._client

    async def health_check(self) -> dict:
        try:
            token = await FeishuAuth.get_tenant_access_token()
            return {"status": "ok", "token_prefix": token[:10] + "..."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: dict | None = None,
        params: dict | None = None,
        headers: dict | None = None,
        timeout: float = 15.0,
    ) -> dict:
        token = await FeishuAuth.get_tenant_access_token()
        default_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        }
        if headers:
            default_headers.update(headers)

        client = await self._get_client()
        resp = await client.request(
            method,
            path,
            headers=default_headers,
            json=json,
            params=params,
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()

        if data.get("code") != 0:
            raise RuntimeError(
                f"Feishu API error: code={data.get('code')}, msg={data.get('msg')}, "
                f"path={path}"
            )
        return data.get("data", {})
