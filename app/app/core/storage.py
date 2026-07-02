"""MinIO / S3-compatible object storage with local filesystem fallback.

业务: 巡检照片等文件上传/下载/删除，MinIO 不可用时自动回退本地存储
依赖: MinIO SDK (可选，未安装时 MINIO_ENABLED 自动为 False)
"""

from __future__ import annotations

import logging
import os
from io import BytesIO

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_client = None  # Minio client
_enabled: bool | None = None
_known_buckets: set[str] = set()
_upload_dir: str = ""


def _init() -> None:
    global _client, _enabled, _upload_dir
    if _enabled is not None:
        return
    settings = get_settings()
    _enabled = settings.MINIO_ENABLED
    _upload_dir = settings.UPLOAD_DIR or "uploads"
    if _enabled:
        try:
            from minio import Minio

            _client = Minio(
                endpoint=settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE,
            )
        except Exception:
            logger.exception("MinIO init failed, falling back to local storage")
            _enabled = False
            _client = None


def _get_client():
    _init()
    return _client if _enabled else None


def _module_bucket(module: str) -> str:
    return f"{get_settings().MINIO_BUCKET_PREFIX}-{module}"


def _ensure_bucket(module: str) -> None:
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


def _local_path(module: str, object_key: str) -> str:
    path = os.path.join(_upload_dir, module, object_key)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def upload_object(
    module: str,
    object_key: str,
    data: bytes,
    length: int,
    content_type: str = "application/octet-stream",
) -> str:
    """上传对象，返回 object_key。MinIO 不可用时写入本地文件。"""
    client = _get_client()
    if client is not None:
        _ensure_bucket(module)
        client.put_object(
            bucket_name=_module_bucket(module),
            object_name=object_key,
            data=BytesIO(data),
            length=length,
            content_type=content_type,
        )
    else:
        path = _local_path(module, object_key)
        with open(path, "wb") as f:
            f.write(data)
    return object_key


def get_object(module: str, object_key: str) -> tuple[bytes, str] | None:
    """读取对象，返回 (data, content_type)；不存在返回 None。"""
    client = _get_client()
    if client is not None:
        try:

            resp = client.get_object(
                bucket_name=_module_bucket(module),
                object_name=object_key,
            )
            data = resp.read()
            ct = resp.getheader("Content-Type") or "application/octet-stream"
            resp.close()
            resp.release_conn()
            return data, ct
        except Exception:
            return None
    else:
        path = _local_path(module, object_key)
        if not os.path.isfile(path):
            return None
        with open(path, "rb") as f:
            return f.read(), "application/octet-stream"


def delete_object(module: str, object_key: str) -> None:
    """删除对象。"""
    client = _get_client()
    if client is not None:
        client.remove_object(
            bucket_name=_module_bucket(module),
            object_name=object_key,
        )
    else:
        path = _local_path(module, object_key)
        if os.path.isfile(path):
            os.remove(path)


def is_enabled() -> bool:
    _init()
    return _enabled or False
