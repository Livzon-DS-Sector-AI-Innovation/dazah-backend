"""OpenAI-compatible LLM HTTP client."""

import json

import httpx


class AIOutputError(Exception):
    """Raised when AI response cannot be parsed into expected structure."""

    def __init__(self, message: str, raw_response: str | None = None):
        self.message = message
        self.raw_response = raw_response
        super().__init__(message)

    def __str__(self) -> str:
        if self.raw_response:
            return f"{self.message} (raw: {self.raw_response[:200]})"
        return self.message


class AIService:
    """OpenAI-compatible LLM client.

    Uses httpx.AsyncClient to call any OpenAI-compatible chat completions API
    (OpenAI, DeepSeek, Qwen, etc.).
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        model: str = "gpt-4o",
        timeout: int = 120,
    ):
        self.model = model
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )

    async def chat(
        self,
        messages: list[dict],
        response_format: str = "json_object",
        temperature: float = 0.1,
        max_tokens: int = 16384,
    ) -> str:
        """Send a chat completion request and return the response text."""
        body: dict = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            body["response_format"] = {"type": response_format}

        resp = await self._client.post("/chat/completions", json=body)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    async def chat_parsed(
        self,
        messages: list[dict],
        expected_keys: list[str],
        temperature: float = 0.1,
    ) -> dict:
        """Chat + parse JSON response, validating expected keys exist."""
        raw = await self.chat(messages, temperature=temperature)
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            raise AIOutputError("AI response is not valid JSON", raw) from e

        # 兼容 AI 返回数组的情况：合并数组中的对象
        if isinstance(parsed, list):
            if len(parsed) == 0:
                raise AIOutputError("AI returned empty list", raw)
            if isinstance(parsed[0], dict):
                merged: dict = {}
                for item in parsed:
                    for k, v in item.items():
                        if k in merged and isinstance(v, str):
                            merged[k] = merged[k] + "；" + v
                        else:
                            merged[k] = v
                parsed = merged
            else:
                parsed = {"_raw": raw}

        # coerce boolean-like strings
        for k, v in parsed.items():
            if isinstance(v, str) and v.lower() in ("true", "false"):
                parsed[k] = v.lower() == "true"

        missing = [k for k in expected_keys if k not in parsed]
        if missing:
            raise AIOutputError(f"AI response missing keys: {missing}", raw)
        return parsed

    async def health_check(self) -> dict:
        """Check connectivity by listing models (lightweight endpoint)."""
        try:
            resp = await self._client.get("/models", timeout=5)
            return {
                "status": "ok" if resp.is_success else "error",
                "detail": str(resp.status_code),
            }
        except Exception as e:
            return {"status": "error", "detail": str(e)}

    async def close(self) -> None:
        await self._client.aclose()
