"""AI 配置共享模块

提供 AI 配置的全局存储，支持数据库持久化。
"""

import json
import os
from typing import Optional

# 全局AI配置（内存缓存）
_ai_config: dict = {
    "minimax_api_key": "",
    "minimax_base_url": "https://api.minimaxi.com/v1",
    "minimax_text_model": "MiniMax-M2.7",
    "minimax_vision_model": "MiniMax-M3",
    "enable_ai_reason": True,
    "enable_ai_scrap": True,
    "enable_ai_analyse": True,
    "enable_ai_label_recognize": True,
    "temperature": 0.7,
    "max_tokens": 1024,
    "timeout": 60,
}

# 数据库配置键
_DB_CONFIG_KEY = "ai_config"
_config_loaded = False


async def _load_config_from_db() -> dict:
    """从数据库加载配置"""
    try:
        from sqlalchemy import text
        from app.core.database import async_session_factory

        async with async_session_factory() as session:
            result = await session.execute(
                text("SELECT config_value FROM qms.qms_ai_config WHERE config_key = :key"),
                {"key": _DB_CONFIG_KEY}
            )
            row = result.fetchone()
            if row and row[0]:
                return json.loads(row[0])
    except Exception as e:
        print(f"[AI Config] 从数据库加载配置失败: {e}")
    return {}


async def _save_config_to_db(config: dict) -> bool:
    """保存配置到数据库"""
    try:
        from sqlalchemy import text
        from app.core.database import async_session_factory

        async with async_session_factory() as session:
            await session.execute(
                text("""
                    UPDATE qms.qms_ai_config
                    SET config_value = :value, updated_at = NOW()
                    WHERE config_key = :key
                """),
                {"key": _DB_CONFIG_KEY, "value": json.dumps(config)}
            )
            await session.commit()
            return True
    except Exception as e:
        print(f"[AI Config] 保存配置到数据库失败: {e}")
        return False


async def load_config_from_db() -> dict:
    """从数据库加载配置到内存（异步初始化）"""
    global _ai_config, _config_loaded
    if not _config_loaded:
        db_config = await _load_config_from_db()
        if db_config:
            _ai_config.update(db_config)
        _config_loaded = True
    return _ai_config.copy()


def get_config() -> dict:
    """获取当前AI配置"""
    return _ai_config.copy()


def update_config(config: dict) -> None:
    """更新AI配置（仅更新内存）"""
    global _ai_config
    _ai_config.update(config)


async def update_config_and_save(config: dict) -> bool:
    """更新AI配置并保存到数据库"""
    global _ai_config
    _ai_config.update(config)
    return await _save_config_to_db(_ai_config)


def get_minimax_api_key() -> str:
    """获取MiniMax API Key"""
    if _ai_config.get("minimax_api_key"):
        return _ai_config["minimax_api_key"]
    return os.getenv("MINIMAX_API_KEY", "")


def get_minimax_base_url() -> str:
    """获取MiniMax API Base URL"""
    if _ai_config.get("minimax_base_url"):
        return _ai_config["minimax_base_url"]
    return os.getenv("MINIMAX_BASE_URL", "https://api.minimaxi.com/v1")


def get_vision_model() -> str:
    """获取视觉识别模型"""
    if _ai_config.get("minimax_vision_model"):
        return _ai_config["minimax_vision_model"]
    return "MiniMax-M3"


def get_text_model() -> str:
    """获取文本生成模型"""
    if _ai_config.get("minimax_text_model"):
        return _ai_config["minimax_text_model"]
    return "MiniMax-M2.7"


def is_label_recognize_enabled() -> bool:
    """检查标签识别功能是否启用"""
    return _ai_config.get("enable_ai_label_recognize", True)