"""千文 (Qwen) API 客户端 — OpenAI 兼容接口。

业务: 巡检照片多模态 AI 分析客户端
依赖: 阿里云 DashScope 兼容接口（凭证见 app.core.config EQUIPMENT_AI_VISION_*）
"""

import httpx

from app.core.config import get_settings


class QwenClient:
    """千文多模态大模型客户端。

    通过阿里云 DashScope OpenAI 兼容接口调用千文 VL 模型，支持图片理解。
    凭证/模型/地址从 config 读取，未配置 API_KEY 时实例化即报明确错误。
    参考: https://help.aliyun.com/zh/model-studio/qwen-vl-api
    """

    def __init__(self, timeout: int | None = None):
        settings = get_settings()
        self.API_KEY = settings.EQUIPMENT_AI_VISION_API_KEY
        self.BASE_URL = settings.EQUIPMENT_AI_VISION_BASE_URL
        self.MODEL = settings.EQUIPMENT_AI_VISION_MODEL
        if not self.API_KEY:
            raise AIAnalysisError(
                "巡检 AI 视觉分析未配置（EQUIPMENT_AI_VISION_API_KEY 为空），"
                "请在 .env 配置后再使用该功能"
            )
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self.API_KEY}",
                "Content-Type": "application/json",
            },
            timeout=timeout or settings.EQUIPMENT_AI_TIMEOUT,
        )

    async def analyze_image(
        self,
        image_base64: str,
        image_mime_type: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
    ) -> str:
        """发送多模态请求，返回 AI 响应文本。

        Args:
            image_base64: 图片的 base64 编码（不含 data:xxx;base64, 前缀）
            image_mime_type: 图片 MIME 类型，如 image/jpeg
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            temperature: 温度参数
        """
        body: dict = {
            "model": self.MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{image_mime_type};base64,{image_base64}"
                            },
                        },
                        {"type": "text", "text": user_prompt},
                    ],
                },
            ],
            "temperature": temperature,
            "max_tokens": 16384,
            "response_format": {"type": "json_object"},
        }

        return await self._request(body)

    async def parse_correction(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
    ) -> str:
        """发送纯文本修正请求，返回 AI 响应文本。

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词（含当前结果和修改说明）
            temperature: 温度参数
        """
        body: dict = {
            "model": self.MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": 16384,
            "response_format": {"type": "json_object"},
        }

        return await self._request(body)

    async def _request(self, body: dict) -> str:
        """发送请求到千文 API，返回响应文本。"""
        resp = await self._client.post("/chat/completions", json=body)
        if resp.is_error:
            detail = ""
            try:
                err_data = resp.json()
                detail = err_data.get("message", "") or str(err_data)
            except Exception:
                detail = resp.text[:500]
            raise AIAnalysisError(
                f"千文 API 返回错误 (HTTP {resp.status_code}): {detail}"
            )
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    async def close(self) -> None:
        await self._client.aclose()


class AIAnalysisError(Exception):
    """AI 分析异常。"""

    def __init__(self, message: str, raw_response: str | None = None):
        self.message = message
        self.raw_response = raw_response
        super().__init__(message)

    def __str__(self) -> str:
        if self.raw_response:
            return f"{self.message} (raw: {self.raw_response[:200]})"
        return self.message
