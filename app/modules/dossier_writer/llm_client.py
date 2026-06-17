"""LLM 客户端 - 兼容 OpenAI API 格式，支持 DeepSeek / 通义千问等"""
import json
from typing import Optional, Dict, Any, List

import httpx

from app.core.config import get_settings


class LLMClient:
    """OpenAI 兼容格式的 LLM 客户端"""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 60.0,
    ):
        settings = get_settings()
        self.base_url = (base_url or settings.LLM_BASE_URL or "").rstrip("/")
        self.api_key = api_key or settings.LLM_API_KEY or ""
        self.model = model or settings.LLM_MODEL or "deepseek-chat"
        self.timeout = timeout

    def is_configured(self) -> bool:
        """检查是否已配置 LLM 服务"""
        return bool(self.base_url and self.api_key)

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        """发送对话请求，返回结构化结果"""
        if not self.is_configured():
            return {
                "success": False,
                "error": "LLM 服务未配置，请在 .env 中设置 LLM_BASE_URL 和 LLM_API_KEY",
                "content": "",
            }

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()

            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})

            return {
                "success": True,
                "content": content,
                "usage": {
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                },
            }
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"LLM API 返回错误: {e.response.status_code} - {e.response.text[:200]}",
                "content": "",
            }
        except httpx.RequestError as e:
            return {
                "success": False,
                "error": f"LLM 请求失败: {str(e)}",
                "content": "",
            }

    async def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
    ) -> Dict[str, Any]:
        """发送对话请求并解析 JSON 响应"""
        result = await self.chat(messages, temperature=temperature)
        if not result["success"]:
            return result

        content = result["content"].strip()
        # 尝试提取 JSON（LLM 可能在 JSON 前后添加 markdown 代码块标记）
        if content.startswith("```"):
            lines = content.split("\n")
            # 去掉首尾的 ``` 行
            json_lines = [
                line
                for line in lines
                if not line.strip().startswith("```")
            ]
            content = "\n".join(json_lines)

        try:
            parsed = json.loads(content)
            result["parsed"] = parsed
            return result
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": f"LLM 返回的内容无法解析为 JSON: {content[:200]}",
                "content": content,
            }


# 全局单例
_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    global _client
    if _client is None:
        _client = LLMClient()
    return _client
