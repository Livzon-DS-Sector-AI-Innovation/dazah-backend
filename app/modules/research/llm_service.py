"""LLM 服务模块 - 支持动态配置管理"""

import json
import os
import re
from pathlib import Path
from typing import Any
import httpx
from dotenv import load_dotenv, set_key, unset_key

# 加载 .env 文件
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)


class LLMConfig:
    """LLM 配置管理类"""
    
    def __init__(self):
        self.reload()
    
    def reload(self):
        """重新加载配置"""
        load_dotenv(env_path, override=True)
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1")
        self.model = os.getenv("OPENAI_MODEL", "deepseek-v4-flash")
    
    def get_config(self) -> dict[str, str]:
        """获取当前配置（隐藏 API Key）"""
        return {
            "api_key": self._mask_key(self.api_key),
            "base_url": self.base_url,
            "model": self.model,
            "is_configured": bool(self.api_key)
        }
    
    def update_config(self, api_key: str = None, base_url: str = None, model: str = None):
        """更新配置并保存到 .env 文件"""
        if api_key is not None:
            # Reject masked keys (prevent saving masked version back to .env)
            if "***" in api_key:
                print("Warning: Ignoring masked API key, not saving to .env")
                return
            
            self.api_key = api_key
            self._save_to_env("OPENAI_API_KEY", api_key)
        
        if base_url is not None:
            self.base_url = base_url
            self._save_to_env("OPENAI_BASE_URL", base_url)
        
        if model is not None:
            self.model = model
            self._save_to_env("OPENAI_MODEL", model)
    
    def _save_to_env(self, key: str, value: str):
        """直接写入 .env 文件，避免 set_key 的截断问题"""
        if not env_path.exists():
            env_path.write_text("")
        
        lines = env_path.read_text().splitlines()
        found = False
        
        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = f"{key}={value}"
                found = True
                break
        
        if not found:
            lines.append(f"{key}={value}")
        
        env_path.write_text("\n".join(lines) + "\n")
    
    def _mask_key(self, key: str) -> str:
        """隐藏 API Key，只显示前10位"""
        if not key:
            return ""
        if len(key) <= 10:
            return key
        return key[:10] + "*" * (len(key) - 10)
    
    async def test_connection(self) -> dict[str, Any]:
        """测试 LLM 连接"""
        if not self.api_key:
            return {"success": False, "message": "❌ API Key 未配置，请输入您的 API Key"}
        
        if not self.api_key.startswith("sk-"):
            return {"success": False, "message": "❌ API Key 格式错误，应以 sk- 开头"}
        
        if len(self.api_key) < 20:
            return {"success": False, "message": "❌ API Key 长度不足，请检查是否完整复制"}
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 5,
                    },
                )
                
                if response.status_code == 200:
                    return {"success": True, "message": f"✅ 连接成功！模型: {self.model}"}
                elif response.status_code == 401:
                    return {"success": False, "message": "❌ API Key 无效，请检查是否正确"}
                elif response.status_code == 404:
                    return {"success": False, "message": f"❌ 模型 {self.model} 不存在，请检查模型名称"}
                elif response.status_code == 429:
                    return {"success": False, "message": "❌ 请求过于频繁，请稍后再试"}
                elif response.status_code >= 500:
                    return {"success": False, "message": f"❌ 服务器错误 ({response.status_code})，请稍后再试"}
                else:
                    error_text = response.text[:100]
                    return {"success": False, "message": f"❌ 请求失败 ({response.status_code}): {error_text}"}
        except httpx.TimeoutException:
            return {"success": False, "message": "❌ 连接超时，请检查网络或 Base URL 是否正确"}
        except httpx.ConnectError:
            return {"success": False, "message": "❌ 无法连接到服务器，请检查 Base URL 是否正确"}
        except Exception as e:
            return {"success": False, "message": f"❌ 未知错误: {str(e)}"}


# 全局配置实例
llm_config = LLMConfig()


async def call_llm(prompt: str, system_prompt: str = "") -> dict:
    """调用 LLM API"""
    if not llm_config.api_key:
        raise ValueError("大语言模型未配置，请先在界面中配置大语言模型")
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{llm_config.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {llm_config.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": llm_config.model,
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


def build_q3c_prompt(steps: list[dict]) -> str:
    """构建 Q3C 溶剂识别 prompt (skill's version with ICH Q3C database)"""
    
    # ICH Q3C Solvent Database
    ich_class1 = ["Benzene", "Carbon tetrachloride", "1,2-Dichloroethane", "1,1-Dichloroethene", "1,1,1-Trichloroethane"]
    
    ich_class2 = [
        "Acetonitrile", "Chlorobenzene", "Chloroform", "Cumene", "Cyclohexane",
        "Cyclopentyl methyl ether", "1,2-Dichloroethene", "Dichloromethane",
        "1,2-Dimethoxyethane", "N,N-Dimethylacetamide", "N,N-Dimethylformamide",
        "1,4-Dioxane", "2-Ethoxyethanol", "Ethyleneglycol", "Formamide", "Hexane",
        "Methanol", "2-Methoxyethanol", "Methylbutyl ketone", "Methylcyclohexane",
        "Methylisobutylketone", "N-Methylpyrrolidone", "Nitromethane", "Pyridine",
        "Sulfolane", "Tertiary-butyl alcohol", "Tetrahydrofuran", "Tetralin",
        "Toluene", "1,1,2-Trichloroethene", "Xylene"
    ]
    
    ich_class3 = [
        "Acetic acid", "Acetone", "Anisole", "1-Butanol", "2-Butanol", "Butyl acetate",
        "tert-Butylmethyl ether", "Dimethyl sulfoxide", "Ethanol", "Ethyl acetate",
        "Ethyl ether", "Ethyl formate", "Formic acid", "Heptane", "Isobutyl acetate",
        "Isopropyl acetate", "Methyl acetate", "3-Methyl-1-butanol", "Methylethyl ketone",
        "2-Methyl-1-propanol", "2-Methyltetrahydrofuran", "Pentane", "1-Pentanol",
        "1-Propanol", "2-Propanol", "Propyl acetate", "Triethylamine"
    ]
    
    # Solvent synonyms (Chinese + English + abbreviations)
    solvent_synonyms = {
        "dichloromethane": ["DCM", "methylene chloride", "二氯甲烷"],
        "dimethylformamide": ["DMF", "N,N-dimethylformamide", "N,N-二甲基甲酰胺"],
        "dimethylsulfoxide": ["DMSO", "二甲基亚砜"],
        "tetrahydrofuran": ["THF", "四氢呋喃"],
        "acetonitrile": ["MeCN", "ACN", "乙腈"],
        "methanol": ["MeOH", "methyl alcohol", "甲醇"],
        "ethanol": ["EtOH", "ethyl alcohol", "乙醇", "无水乙醇"],
        "isopropanol": ["IPA", "isopropyl alcohol", "2-propanol", "异丙醇"],
        "acetone": ["propanone", "丙酮"],
        "ethyl acetate": ["EtOAc", "乙酸乙酯"],
        "toluene": ["methylbenzene", "甲苯"],
        "benzene": ["苯"],
        "chloroform": ["trichloromethane", "氯仿"],
        "carbon tetrachloride": ["四氯化碳"],
        "1,2-dichloroethane": ["DCE", "1,2-二氯乙烷"],
        "1,4-dioxane": ["dioxane", "1,4-二氧六环"],
        "n-methyl-2-pyrrolidone": ["NMP", "N-甲基吡咯烷酮"],
        "pyridine": ["吡啶"],
        "hexane": ["n-hexane", "正己烷"],
        "heptane": ["n-heptane", "正庚烷"],
        "cyclohexane": ["环己烷"],
        "diethyl ether": ["ether", "乙醚"],
        "tert-butyl methyl ether": ["MTBE", "甲基叔丁基醚"],
        "2-methyltetrahydrofuran": ["2-MeTHF", "2-甲基四氢呋喃"],
        "trichloroethylene": ["TCE", "三氯乙烯"],
        "tetrachloroethylene": ["PERC", "四氯乙烯"],
        "1,1,1-trichloroethane": ["1,1,1-三氯乙烷"],
        "chlorobenzene": ["monochlorobenzene", "氯苯"],
        "xylene": ["xylenes", "二甲苯"],
        "o-xylene": ["邻二甲苯"],
        "m-xylene": ["间二甲苯"],
        "p-xylene": ["对二甲苯"],
        "n,n-dimethylacetamide": ["DMA", "DMAc", "N,N-二甲基乙酰胺"],
        "triethylamine": ["TEA", "三乙胺"],
        "methyl isobutyl ketone": ["MIBK", "甲基异丁基酮"],
        "ethyl methyl ketone": ["MEK", "butanone", "丁酮"],
        "tert-butanol": ["t-butanol", "叔丁醇"],
        "ethylene glycol": ["乙二醇"],
        "glycerol": ["glycerin", "甘油"],
        "formic acid": ["甲酸"],
        "acetic acid": ["乙酸"],
        "trifluoroacetic acid": ["TFA", "三氟乙酸"],
        "sulfuric acid": ["硫酸"],
        "hydrochloric acid": ["HCl", "盐酸"],
        "nitric acid": ["硝酸"],
        "phosphoric acid": ["磷酸"]
    }
    
    prompt = f"""你是一个制药工艺分析专家。请从以下合成工艺步骤中提取所有使用的溶剂，并根据 ICH Q3C(R9) 指南进行分类。

## 任务
1. 识别每个步骤中作为溶剂使用的有机挥发性化学品
2. 将每个溶剂与 ICH Q3C 数据库匹配
3. 确定 ICH 分类 (Class 1/2/3) 或标记为未列出

## ICH Q3C 溶剂数据库

### Class 1 - 避免使用 (已知致癌物)
{", ".join(ich_class1)}

### Class 2 - 限制使用 (动物致癌物或不可逆毒性)
{", ".join(ich_class2)}

### Class 3 - 低毒潜在 (PDE ≥ 50 mg/天)
{", ".join(ich_class3)}

## 溶剂同义词参考

以下是常见溶剂的中文/英文/缩写名称 (匹配时请考虑所有这些变体):
"""
    
    for canonical, synonyms in solvent_synonyms.items():
        prompt += f"- {canonical}: {', '.join(synonyms)}\n"
    
    prompt += """
## 匹配规则

**重要**: 当匹配溶剂时:
1. **忽略浓度前缀**: 95% 乙醇、无水乙醇、Absolute ethanol → 都匹配到 Ethanol
2. **考虑多语言名称**: 
   - 中文名：乙醇，二氯甲烷，四氢呋喃
   - 英文名：Ethanol, Dichloromethane, Tetrahydrofuran
   - 缩写：DCM, THF, EtOH, MeOH
3. **匹配优先级**:
   - 先检查同义词表 → 找到规范名
   - 再用规范名匹配 ICH 数据库
   - 如果仍无匹配 → 标记为 "Unlisted"

## 区分标准

**溶剂** (需要提取):
- 作为反应介质
- 作为萃取溶剂
- 作为纯化/重结晶溶剂
- 作为洗涤溶剂
- 有机挥发性化学品

**不是溶剂** (忽略):
- 纯化水/注射用水 (水不是 ICH Q3C 监管的溶剂)
- 氨水、氢氧化钠溶液等 pH 调节试剂
- 固体试剂 (即使溶解在其他溶剂中)
- 反应物/底物/产物
- 催化剂 (除非同时作为溶剂使用)
- 干燥剂 (如无水硫酸钠)

## 输出格式

返回 JSON 格式，结构如下:
{
  "steps": [
    {
      "step_number": "Step 1",
      "step_title": "步骤标题",
      "solvents": [
        {
          "original_name": "原文中的溶剂名称 (如：95% 乙醇)",
          "matched_name": "匹配到的 ICH 规范名 (如：Ethanol)",
          "ich_class": "Class 1/2/3 或 Unlisted",
          "purpose": "反应/萃取/纯化/洗涤",
          "amount": "用量 (如果有，没有则为 null)"
        }
      ]
    }
  ]
}

## 示例

输入文本："使用 95% 乙醇进行重结晶"
输出：
{
  "original_name": "95% 乙醇",
  "matched_name": "Ethanol",
  "ich_class": "Class 3",
  "purpose": "纯化",
  "amount": null
}

输入文本："加入 DCM 萃取"
输出：
{
  "original_name": "DCM",
  "matched_name": "Dichloromethane",
  "ich_class": "Class 2",
  "purpose": "萃取",
  "amount": null
}

## 工艺步骤文本
"""
    
    # Add each step's content
    for step in steps:
        step_text = step.get("content", "")
        prompt += f"\n\n{step.get('title', 'Step')}: {step_text}\n"
    
    prompt += "\n\n请只返回 JSON，不要其他解释。确保每个溶剂都包含 ich_class 字段。"
    
    return prompt


async def extract_elements_with_llm(text: str) -> list[dict]:
    """使用 LLM 从文本中提取元素"""
    prompt = build_q3d_prompt(text)
    result = await call_llm(prompt)
    return result.get("elements", [])


async def extract_solvents_with_llm(steps: list[dict]) -> dict:
    """使用 LLM 从工艺步骤中提取溶剂并分类 (skill's version)
    
    Args:
        steps: List of parsed process steps from ich_service.parse_process_steps
        
    Returns:
        Full LLM response with steps structure
    """
    prompt = build_q3c_prompt(steps)
    result = await call_llm(prompt)
    return result
