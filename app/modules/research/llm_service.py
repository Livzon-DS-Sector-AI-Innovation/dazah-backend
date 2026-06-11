"""LLM 服务模块 - 使用 httpx 直接调用 OpenAI API"""

import json
import os
from pathlib import Path
from typing import Any
import httpx
from dotenv import load_dotenv

# 加载 .env 文件
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)

# OpenAI API 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "deepseek-v4-flash")


async def call_llm(prompt: str, system_prompt: str = "") -> dict:
    """调用 LLM API"""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY 未配置")
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{OPENAI_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": OPENAI_MODEL,
                "messages": messages,
                "temperature": 0.1,
                "response_format": {"type": "json_object"},
            },
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)


def build_q3d_prompt(text: str) -> str:
    """构建 Q3D 元素识别 prompt"""
    return f"""你是一个制药工艺分析专家。请从以下药品合成工艺文本中提取所有需要评估的元素杂质。

## 任务
1. 识别文本中提到的所有元素（催化剂、试剂、设备来源等）
2. 确定每个元素的来源
3. 判断是否为有意添加（催化剂/试剂 vs 设备/杂质）

## 文本内容
{text}

## 输出格式
请输出 JSON 格式：
{{
  "elements": [
    {{
      "symbol": "元素符号（如 Pd, Ni, Co 等）",
      "source": "来源描述（如：钯碳催化剂、不锈钢反应器等）",
      "intentionally_added": true/false
    }}
  ]
}}

注意：
- 只输出 JSON，不要输出其他内容
- 如果文本中没有提到任何元素，返回 {{"elements": []}}
- symbol 必须是标准的元素符号
"""


def build_q3c_prompt(text: str) -> str:
    """构建 Q3C 溶剂识别 prompt"""
    return f"""你是一个制药工艺分析专家。请从以下药品合成工艺文本中提取所有使用的溶剂。

## 任务
1. 识别每个步骤中作为溶剂使用的有机挥发性化学品
2. 忽略水、酸碱试剂、固体试剂
3. 忽略浓度前缀（95%乙醇→乙醇，无水乙醇→乙醇）

## 区分标准

**溶剂**（需要提取）：
- 作为反应介质
- 作为萃取溶剂
- 作为纯化/重结晶溶剂
- 作为洗涤溶剂

**不是溶剂**（忽略）：
- 纯化水/注射用水
- 氨水、氢氧化钠溶液等 pH 调节试剂
- 固体试剂
- 反应物/底物/产物
- 催化剂（除非同时作为溶剂使用）

## 文本内容
{text}

## 输出格式
请输出 JSON 格式：
{{
  "solvents": [
    {{
      "name": "溶剂名称（中文或英文）",
      "purpose": "用途（反应/萃取/洗涤/重结晶等）"
    }}
  ]
}}

注意：
- 只输出 JSON，不要输出其他内容
- 如果没有找到溶剂，返回 {{"solvents": []}}
- 忽略浓度前缀，如 95%乙醇 输出为 乙醇
"""


async def extract_elements_with_llm(text: str) -> list[dict]:
    """使用 LLM 从文本中提取元素"""
    try:
        prompt = build_q3d_prompt(text)
        result = await call_llm(prompt)
        return result.get("elements", [])
    except Exception as e:
        print(f"LLM 调用失败: {e}")
        return []


async def extract_solvents_with_llm(text: str) -> list[dict]:
    """使用 LLM 从文本中提取溶剂"""
    try:
        prompt = build_q3c_prompt(text)
        result = await call_llm(prompt)
        return result.get("solvents", [])
    except Exception as e:
        print(f"LLM 调用失败: {e}")
        return []
