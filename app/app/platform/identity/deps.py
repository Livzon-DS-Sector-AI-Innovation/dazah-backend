from typing import Annotated

from fastapi import Depends, Request

from app.platform.identity.models import User


async def get_current_user(request: Request) -> User | None:
    """Phase 1 keeps authentication optional.

    Phase 2 can replace this with Feishu SSO token parsing while preserving the
    dependency contract used by route handlers.
    """
    return None


CurrentUser = Annotated[User | None, Depends(get_current_user)]
