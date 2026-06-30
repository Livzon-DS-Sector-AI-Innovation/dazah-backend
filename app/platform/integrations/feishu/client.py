"""Feishu HTTP client with auth and retry."""

import httpx

from app.platform.integrations.base import IntegrationClient
from app.platform.integrations.feishu.auth import FeishuAuth



from dataclasses import dataclass
from typing import Optional


@dataclass
class FeishuTokenResponse:
    """飞书 user_access_token 响应"""
    access_token: str
    expires_in: int
    token_type: str = "Bearer"
    refresh_token: Optional[str] = None
    refresh_token_expires_in: Optional[int] = None
    scope: Optional[str] = None
    code: int = 0
    msg: str = ""

    def success(self) -> bool:
        return self.code == 0 and bool(self.access_token)


@dataclass
class FeishuUserInfo:
    """飞书用户信息"""
    open_id: str = ""
    user_id: str = ""
    name: str = ""
    en_name: str = ""
    email: str = ""
    mobile: str = ""
    avatar_url: str = ""
    employee_no: str = ""
    tenant_key: str = ""
    union_id: str = ""


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


    async def exchange_code(self, code: str) -> FeishuTokenResponse:
        """用授权码换取 user_access_token"""
        from app.core.config import get_settings
        import logging
        logger = logging.getLogger(__name__)
        settings = get_settings()
        
        logger.info(f"Exchanging code for token, redirect_uri={settings.FEISHU_REDIRECT_URI}")
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://open.feishu.cn/open-apis/authen/v2/oauth/token",
                json={
                    "grant_type": "authorization_code",
                    "client_id": settings.FEISHU_APP_ID,
                    "client_secret": settings.FEISHU_APP_SECRET,
                    "code": code,
                    "redirect_uri": settings.FEISHU_REDIRECT_URI,
                },
                timeout=10.0,
            )
            
            logger.info(f"Token exchange response: status={resp.status_code}, body={resp.text[:500]}")
            
            # Don't raise on 400 - parse the error from response body
            if resp.status_code != 200:
                try:
                    data = resp.json()
                    return FeishuTokenResponse(
                        access_token="",
                        expires_in=0,
                        code=data.get("code", resp.status_code),
                        msg=data.get("error_description", data.get("msg", f"HTTP {resp.status_code}")),
                    )
                except Exception:
                    return FeishuTokenResponse(
                        access_token="",
                        expires_in=0,
                        code=resp.status_code,
                        msg=f"HTTP {resp.status_code}: {resp.text[:200]}",
                    )
            
            data = resp.json()
        
        if data.get("code") != 0:
            return FeishuTokenResponse(
                access_token="",
                expires_in=0,
                code=data.get("code", -1),
                msg=data.get("error_description", data.get("msg", "Unknown error")),
            )
        
        return FeishuTokenResponse(
            access_token=data.get("access_token", ""),
            expires_in=data.get("expires_in", 0),
            token_type=data.get("token_type", "Bearer"),
            refresh_token=data.get("refresh_token"),
            refresh_token_expires_in=data.get("refresh_token_expires_in"),
            scope=data.get("scope"),
        )

    async def get_user_info(self, access_token: str) -> FeishuUserInfo:
        """用 user_access_token 获取用户信息"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://open.feishu.cn/open-apis/authen/v1/user_info",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10.0,
            )
            resp.raise_for_status()
            data = resp.json()
        
        if data.get("code") != 0:
            raise RuntimeError(f"Failed to get user info: {data.get('msg')}")
        
        user_data = data.get("data", {})
        return FeishuUserInfo(
            open_id=user_data.get("open_id", ""),
            user_id=user_data.get("user_id", ""),
            name=user_data.get("name", ""),
            en_name=user_data.get("en_name", ""),
            email=user_data.get("email", ""),
            mobile=user_data.get("mobile", ""),
            avatar_url=user_data.get("avatar_url", ""),
            employee_no=user_data.get("employee_no", ""),
            tenant_key=user_data.get("tenant_key", ""),
            union_id=user_data.get("union_id", ""),
        )

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
