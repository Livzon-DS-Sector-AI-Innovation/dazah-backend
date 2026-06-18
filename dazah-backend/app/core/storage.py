"""文件存储工具类

提供本地文件上传和存储功能。
"""

import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import UploadFile

# 上传目录配置
UPLOAD_DIR = Path("uploads")
REAGENT_LABELS_DIR = UPLOAD_DIR / "reagent-labels"

# 允许的文件类型
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


async def save_upload_file(file: UploadFile, sub_dir: Optional[str] = None) -> str:
    """保存单个上传的文件

    Args:
        file: 上传的文件对象
        sub_dir: 子目录名称

    Returns:
        文件访问 URL 路径

    Raises:
        ValueError: 文件类型不支持或文件过大
    """
    # 检查文件扩展名
    ext = Path(file.filename).suffix.lower() if file.filename else ".jpg"
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"不支持的文件类型: {ext}，支持的类型: {', '.join(ALLOWED_EXTENSIONS)}")

    # 生成唯一文件名
    unique_filename = f"{uuid.uuid4()}{ext}"

    # 确定保存目录
    if sub_dir:
        save_dir = UPLOAD_DIR / sub_dir
    else:
        save_dir = UPLOAD_DIR

    # 创建目录
    save_dir.mkdir(parents=True, exist_ok=True)

    # 保存文件
    file_path = save_dir / unique_filename
    content = await file.read()

    # 检查文件大小
    if len(content) > MAX_FILE_SIZE:
        raise ValueError(f"文件大小超过限制 ({MAX_FILE_SIZE // (1024 * 1024)}MB)")

    with open(file_path, "wb") as f:
        f.write(content)

    # 返回相对 URL 路径
    return f"/uploads/{sub_dir}/{unique_filename}" if sub_dir else f"/uploads/{unique_filename}"


async def save_upload_files(files: list[UploadFile], sub_dir: str = "reagent-labels") -> list[str]:
    """保存多个上传的文件

    Args:
        files: 上传的文件列表
        sub_dir: 子目录名称

    Returns:
        文件访问 URL 路径列表
    """
    urls = []
    for file in files:
        try:
            url = await save_upload_file(file, sub_dir)
            urls.append(url)
        except Exception as e:
            # 继续处理其他文件，记录错误
            print(f"保存文件 {file.filename} 失败: {e}")
            continue

    return urls


def delete_upload_file(file_url: str) -> bool:
    """删除上传的文件

    Args:
        file_url: 文件访问 URL 路径

    Returns:
        是否删除成功
    """
    try:
        # 将 URL 路径转换为实际文件路径
        if file_url.startswith("/uploads/"):
            relative_path = file_url[10:]  # 去掉 "/uploads/" 前缀
        else:
            relative_path = file_url

        file_path = UPLOAD_DIR / relative_path

        if file_path.exists():
            file_path.unlink()
            return True
        return False
    except Exception as e:
        print(f"删除文件失败: {e}")
        return False


def get_file_path(file_url: str) -> Optional[Path]:
    """获取文件的实际路径

    Args:
        file_url: 文件访问 URL 路径

    Returns:
        文件实际路径，如果文件不存在返回 None
    """
    if file_url.startswith("/uploads/"):
        relative_path = file_url[10:]
    else:
        relative_path = file_url

    file_path = UPLOAD_DIR / relative_path

    if file_path.exists():
        return file_path
    return None