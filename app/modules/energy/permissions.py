"""能源模块权限声明。"""

from app.platform.permission.registry import PermissionDef

PERMISSIONS: list[PermissionDef] = [
    PermissionDef("energy:overview:read", "查看能源总览", "energy", "overview", "read"),
    PermissionDef("energy:device:read", "查看数据源", "energy", "device", "read"),
    PermissionDef("energy:device:manage", "管理数据源", "energy", "device", "manage"),
    PermissionDef("energy:alert:read", "查看预警", "energy", "alert", "read"),
    PermissionDef("energy:alert:manage", "管理预警", "energy", "alert", "manage"),
    PermissionDef(
        "energy:collect_log:read", "查看采集日志", "energy", "collect_log", "read"
    ),
]
