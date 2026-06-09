"""Feishu HTTP client with auth and retry."""

import httpx

from app.platform.integrations.base import IntegrationClient
from app.platform.integrations.feishu.auth import FeishuAuth


class FeishuClient(IntegrationClient):
    system_name = "feishu"
    base_url = "https://open.feishu.cn/open-apis"

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
        timeout: float = 15.0,
    ) -> dict:
        token = await FeishuAuth.get_tenant_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        }

        async with httpx.AsyncClient(base_url=self.base_url) as client:
            resp = await client.request(
                method,
                path,
                headers=headers,
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

    def build_authorize_url(self, state: str) -> str:
        """Build Feishu OAuth authorize URL."""
        from app.core.config import get_settings
        settings = get_settings()
        
        redirect_uri = settings.FEISHU_REDIRECT_URI
        app_id = settings.FEISHU_APP_ID
        
        return (
            f"https://open.feishu.cn/open-apis/authen/v1/authorize"
            f"?app_id={app_id}"
            f"&redirect_uri={redirect_uri}"
            f"&state={state}"
        )
