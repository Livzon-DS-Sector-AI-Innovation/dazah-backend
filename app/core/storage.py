"""MinIO / S3-compatible object storage service — 模块级 bucket 隔离。

每个模块拥有独立 bucket：{MINIO_BUCKET_PREFIX}-{module}
例如 dazah-equipment、dazah-production、dazah-quality。

Usage:
    from app.core.storage import upload_object, presigned_get_url, delete_object, is_enabled

    if is_enabled():
        upload_object("equipment", "inspection/abc.jpg", data, len(data), "image/jpeg")
        url = presigned_get_url("equipment", "inspection/abc.jpg")
        delete_object("equipment", "inspection/abc.jpg")
"""

from __future__ import annotations

import logging
from datetime import timedelta
from io import BytesIO

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_client: "Minio | None" = None  # type: ignore[name-defined]
_enabled: bool | None = None
_known_buckets: set[str] = set()  # 已确认存在的 bucket，避免重复检查


def _get_client() -> "Minio | None":  # type: ignore[name-defined]
    """延迟初始化 MinIO 客户端."""
    global _client, _enabled

    if _enabled is None:
        settings = get_settings()
        _enabled = settings.MINIO_ENABLED
        if _enabled:
            from minio import Minio

            _client = Minio(
                endpoint=settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE,
            )

    return _client if _enabled else None


def _module_bucket(module: str) -> str:
    """生成模块专属 bucket 名称：{prefix}-{module}。"""
    prefix = get_settings().MINIO_BUCKET_PREFIX
    return f"{prefix}-{module}"


def _ensure_bucket(module: str) -> None:
    """确保模块的 bucket 存在（每个模块首次使用时自动创建）。"""
    client = _get_client()
    if client is None:
        return

    bucket = _module_bucket(module)
    if bucket in _known_buckets:
        return

    try:
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
            logger.info("Created MinIO bucket: %s", bucket)
        _known_buckets.add(bucket)
    except Exception:
        logger.exception("Failed to ensure MinIO bucket: %s", bucket)


def upload_object(
    module: str,
    object_key: str,
    data: bytes,
    length: int,
    content_type: str = "application/octet-stream",
) -> str:
    """上传对象到模块专属 bucket，返回 object_key。"""
    client = _get_client()
    if client is None:
        raise RuntimeError("MinIO is not enabled. Set MINIO_ENABLED=true")

    _ensure_bucket(module)
    bucket = _module_bucket(module)
    client.put_object(
        bucket_name=bucket,
        object_name=object_key,
        data=BytesIO(data),
        length=length,
        content_type=content_type,
    )
    return object_key


def presigned_get_url(
    module: str, object_key: str, expires_seconds: int = 3600
) -> str:
    """生成预签名下载 URL（有效期默认 1 小时）。"""
    client = _get_client()
    if client is None:
        raise RuntimeError("MinIO is not enabled")

    bucket = _module_bucket(module)
    return client.presigned_get_object(
        bucket_name=bucket,
        object_name=object_key,
        expires=timedelta(seconds=expires_seconds),
    )


def delete_object(module: str, object_key: str) -> None:
    """从模块专属 bucket 删除对象。"""
    client = _get_client()
    if client is None:
        raise RuntimeError("MinIO is not enabled")

    bucket = _module_bucket(module)
    client.remove_object(bucket_name=bucket, object_name=object_key)


def is_enabled() -> bool:
    """检查 MinIO 是否已启用。"""
    return _get_client() is not None
