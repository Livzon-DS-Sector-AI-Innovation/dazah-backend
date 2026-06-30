import datetime
import json
import logging

import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.platform.identity.models import User
from app.platform.identity.repository import UserRepository
from app.platform.integrations.feishu.client import FeishuClient

logger = logging.getLogger(__name__)


class IdentityService:
    def __init__(
        self,
        settings: Settings,
        feishu_client: FeishuClient,
        user_repo: UserRepository,
    ) -> None:
        self._settings = settings
        self._feishu = feishu_client
        self._user_repo = user_repo

    def build_login_url(self, state: str) -> str:
        return self._feishu.build_authorize_url(state)

    async def handle_callback(
        self, session: AsyncSession, code: str,
    ) -> str:
        """Exchange code → get user info → upsert user → enrich department/position → return JWT."""
        # Step 1: Exchange authorization code for user_access_token
        token_resp = await self._feishu.exchange_code(code)
        if not token_resp.success():
            raise RuntimeError(
                f"Feishu token exchange failed: code={token_resp.code}, msg={token_resp.msg}",
            )

        # Step 2: Get user info using user_access_token
        user_info = await self._feishu.get_user_info(token_resp.access_token)
        
        feishu_open_id = user_info.open_id
        feishu_user_id = user_info.user_id

        user = await self._user_repo.get_by_feishu_open_id(session, feishu_open_id)
        if user is None:
            user = await self._user_repo.create(
                session,
                name=user_info.name or "",
                feishu_user_id=feishu_user_id,
                feishu_open_id=feishu_open_id,
                employee_no=user_info.employee_no or None,
                email=user_info.email or None,
                mobile=user_info.mobile or None,
                avatar_url=user_info.avatar_url or None,
            )
        else:
            user.name = user_info.name or user.name
            user.email = user_info.email or user.email
            user.mobile = user_info.mobile or user.mobile
            user.avatar_url = user_info.avatar_url or user.avatar_url

        # ── 补全部门/职位信息 ──
        if feishu_user_id and (
            not user.department or not user.position or not user.feishu_department_ids
        ):
            try:
                from app.platform.integrations.feishu.contact import get_user_detail

                detail = await get_user_detail(feishu_user_id, user_id_type="user_id")
                if detail:
                    if detail.get("department_ids"):
                        user.feishu_department_ids = json.dumps(
                            detail["department_ids"], ensure_ascii=False,
                        )
                    if detail.get("positions"):
                        major = next(
                            (p for p in detail["positions"] if p.get("is_major")),
                            None,
                        )
                        if major:
                            if major.get("position_name"):
                                user.position = major["position_name"]
                    elif detail.get("job_title"):
                        user.position = detail["job_title"]
            except Exception:
                logger.exception("Failed to enrich user detail for %s", feishu_user_id)

        await session.flush()
        return self._generate_jwt(user)

    def _generate_jwt(self, user: User) -> str:
        payload = {
            "sub": str(user.id),
            "open_id": user.feishu_open_id,
            "iat": datetime.datetime.now(tz=datetime.UTC),
            "exp": datetime.datetime.now(tz=datetime.UTC)
            + datetime.timedelta(seconds=self._settings.JWT_EXPIRE_SECONDS),
        }
        return jwt.encode(
            payload,
            self._settings.SECRET_KEY,
            algorithm="HS256",
        )

    def verify_jwt(self, token: str) -> dict:
        return jwt.decode(
            token,
            self._settings.SECRET_KEY,
            algorithms=["HS256"],
        )
