"""Authentication service — handles OAuth callback, JWT generation, user upsert."""

from __future__ import annotations

import logging
import secrets
from datetime import UTC, datetime, timedelta
from hashlib import pbkdf2_hmac
from hmac import compare_digest

import jwt
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import async_session_factory
from app.platform.identity.models import User
from app.platform.identity.repository import UserRepository
from app.platform.integrations.feishu.oauth import FeishuOAuthClient

logger = logging.getLogger(__name__)

_repo = UserRepository()
_PASSWORD_ITERATIONS = 260_000
SYSTEM_ADMIN_USERNAME = "system_admin"
SYSTEM_ADMIN_NAME = "系统管理员"


def hash_password(password: str) -> str:
    """Hash a local-account password using PBKDF2-SHA256."""
    salt = secrets.token_bytes(16)
    digest = pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, _PASSWORD_ITERATIONS
    )
    return (
        f"pbkdf2_sha256${_PASSWORD_ITERATIONS}$"
        f"{salt.hex()}${digest.hex()}"
    )


def verify_password(password: str, stored_hash: str | None) -> bool:
    if not stored_hash:
        return False
    try:
        algorithm, iterations, salt_hex, digest_hex = stored_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        expected = pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iterations),
        ).hex()
    except (ValueError, TypeError):
        return False
    return compare_digest(expected, digest_hex)


def _split_identifiers(raw: str) -> set[str]:
    return {item.strip().lower() for item in raw.split(",") if item.strip()}


def _matches_admin_whitelist(user: User, raw_identifiers: str) -> bool:
    identifiers = _split_identifiers(raw_identifiers)
    if not identifiers:
        return False
    candidates = {
        user.username,
        user.feishu_open_id,
        user.feishu_user_id,
        user.email,
        user.enterprise_email,
        user.mobile,
        user.employee_no,
    }
    return any(value and value.lower() in identifiers for value in candidates)


async def handle_oauth_callback(
    db: AsyncSession,
    code: str,
) -> tuple[User, str]:
    """Complete the OAuth flow: exchange code → get user info → upsert → JWT.

    Returns (user, jwt_token).
    """
    oauth = FeishuOAuthClient.from_settings()

    # 1. Exchange authorization code for tokens (v2 endpoint)
    token_data = await oauth.exchange_code(code)
    user_access_token = token_data["access_token"]

    # 2. Fetch user profile from Feishu (v1 user_info endpoint)
    #    Response fields: name, en_name, avatar_url, avatar_thumb,
    #    avatar_middle, avatar_big, open_id, union_id, email,
    #    enterprise_email, user_id, mobile, tenant_key
    info = await oauth.get_user_info(user_access_token)

    open_id = info.get("open_id", "")
    user_id = info.get("user_id") or None  # Convert empty to None
    union_id = info.get("union_id") or None  # Convert empty to None
    name = info.get("name", "")
    en_name = info.get("en_name")
    avatar_url = info.get("avatar_url") or info.get("avatar_middle")
    avatar_thumb = info.get("avatar_thumb")
    avatar_middle = info.get("avatar_middle")
    avatar_big = info.get("avatar_big")
    email = info.get("email") or info.get("enterprise_email")
    enterprise_email = info.get("enterprise_email")
    mobile = info.get("mobile")
    tenant_key = info.get("tenant_key")

    if not open_id:
        raise ValueError("Feishu user info missing open_id")

    # 3. Upsert user in local DB
    user = await _repo.get_by_feishu_open_id(db, open_id)
    if user is None:
        # Also try matching by feishu_user_id in case user was synced earlier
        user = await _repo.get_by_feishu_user_id(db, user_id) if user_id else None

    if user is None:
        user = await _repo.create(
            db,
            name=name,
            feishu_user_id=user_id,
            feishu_open_id=open_id,
            feishu_union_id=union_id,
            en_name=en_name,
            email=email,
            enterprise_email=enterprise_email,
            mobile=mobile,
            avatar_url=avatar_url,
            avatar_thumb=avatar_thumb,
            avatar_middle=avatar_middle,
            avatar_big=avatar_big,
            tenant_key=tenant_key,
            role="admin"
            if _matches_admin_whitelist(
                User(
                    name=name,
                    feishu_user_id=user_id,
                    feishu_open_id=open_id,
                    email=email,
                    enterprise_email=enterprise_email,
                    mobile=mobile,
                ),
                get_settings().SSO_ADMIN_IDENTIFIERS,
            )
            else "user",
            status="active",
            auth_source="feishu",
        )
        logger.info("Created new user: %s (open_id=%s)", name, open_id)
    else:
        # Update profile info on each login
        user.name = name or user.name
        user.feishu_user_id = user_id or user.feishu_user_id
        user.feishu_union_id = union_id or user.feishu_union_id
        user.en_name = en_name or user.en_name
        user.email = email or user.email
        user.enterprise_email = enterprise_email or user.enterprise_email
        user.mobile = mobile or user.mobile
        user.avatar_url = avatar_url or user.avatar_url
        user.avatar_thumb = avatar_thumb or user.avatar_thumb
        user.avatar_middle = avatar_middle or user.avatar_middle
        user.avatar_big = avatar_big or user.avatar_big
        user.tenant_key = tenant_key or user.tenant_key
        user.auth_source = user.auth_source or "feishu"
        if _matches_admin_whitelist(user, get_settings().SSO_ADMIN_IDENTIFIERS):
            user.role = "admin"
        logger.info("Updated user: %s (open_id=%s)", user.name, open_id)

    if user.status == "disabled":
        raise PermissionError("User account is disabled")
    user.last_login_at = datetime.now(UTC)
    await db.commit()

    # 4. Generate JWT
    token = generate_jwt(user)
    return user, token


def generate_jwt(user: User) -> str:
    """Generate a JWT token for the given user."""
    settings = get_settings()
    now = datetime.now(UTC)
    payload = {
        "sub": str(user.id),
        "open_id": user.feishu_open_id,
        "name": user.name,
        "role": user.role,
        "auth_source": user.auth_source,
        "iat": now,
        "exp": now + timedelta(seconds=settings.JWT_EXPIRE_SECONDS),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


async def authenticate_local_user(
    db: AsyncSession, *, username: str, password: str
) -> tuple[User, str]:
    user = await _repo.get_by_login_identifier(db, username)
    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "用户名或密码错误")
    if user.status == "disabled":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "账号已禁用")
    user.last_login_at = datetime.now(UTC)
    await db.flush()
    return user, generate_jwt(user)


async def bootstrap_local_users() -> None:
    settings = get_settings()
    entries = [
        (
            settings.BOOTSTRAP_ADMIN_USERNAME,
            settings.BOOTSTRAP_ADMIN_PASSWORD,
            settings.BOOTSTRAP_ADMIN_NAME,
            settings.BOOTSTRAP_ADMIN_EMAIL,
            "admin",
        ),
        (
            settings.BOOTSTRAP_USER_USERNAME,
            settings.BOOTSTRAP_USER_PASSWORD,
            settings.BOOTSTRAP_USER_NAME,
            settings.BOOTSTRAP_USER_EMAIL,
            "user",
        ),
    ]

    async with async_session_factory() as session:
        for username, password, name, email, role in entries:
            if not username or not password:
                continue
            existing = await _repo.get_by_username(session, username)
            if existing is None:
                await _repo.create(
                    session,
                    username=username,
                    password_hash=hash_password(password),
                    name=name or username,
                    email=email or None,
                    role=role,
                    status="active",
                    auth_source="local",
                )
                logger.info("Bootstrapped %s local user: %s", role, username)
                continue

            existing.password_hash = hash_password(password)
            existing.name = name or existing.name
            existing.email = email or existing.email
            existing.role = role
            existing.status = "active"
            existing.auth_source = existing.auth_source or "local"

        await get_or_create_system_admin(session)
        await session.commit()


async def get_or_create_system_admin(db: AsyncSession) -> User:
    """Return the platform default administrator used when login is disabled."""
    user = await _repo.get_by_username_including_deleted(db, SYSTEM_ADMIN_USERNAME)
    if user is None:
        user = await _repo.create(
            db,
            username=SYSTEM_ADMIN_USERNAME,
            name=SYSTEM_ADMIN_NAME,
            role="admin",
            status="active",
            auth_source="local",
        )
        logger.info("Created default platform administrator: %s", SYSTEM_ADMIN_USERNAME)
        return user

    changed = False
    if user.name != SYSTEM_ADMIN_NAME:
        user.name = SYSTEM_ADMIN_NAME
        changed = True
    if user.role != "admin":
        user.role = "admin"
        changed = True
    if user.status != "active":
        user.status = "active"
        changed = True
    if user.auth_source != "local":
        user.auth_source = "local"
        changed = True
    if user.is_deleted:
        user.is_deleted = False
        changed = True

    if changed:
        await db.flush()
    return user


def generate_state_token() -> str:
    """Generate a short-lived state token for CSRF protection."""
    import secrets
    settings = get_settings()
    nonce = secrets.token_urlsafe(32)
    now = datetime.now(UTC)
    payload = {
        "nonce": nonce,
        "iat": now,
        "exp": now + timedelta(minutes=5),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def validate_state_token(state: str) -> bool:
    """Validate a state token. Returns True if valid and not expired."""
    settings = get_settings()
    try:
        jwt.decode(state, settings.SECRET_KEY, algorithms=["HS256"])
        return True
    except jwt.InvalidTokenError:
        return False
