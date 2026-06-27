"""生产模块权限声明。"""

from app.platform.permission.registry import PermissionDef

PERMISSIONS: list[PermissionDef] = [
    PermissionDef(
        "production:batch:read", "查看生产批次", "production", "batch", "read"
    ),
]
