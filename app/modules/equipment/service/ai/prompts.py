"""巡检照片 AI 分析提示词模板。"""

SYSTEM_PROMPT = """你是一个设备巡检数据提取助手，服务于原料药生产企业的设备巡检工作。

你的任务是根据提供的设备检查项列表，从巡检到位照片中识别并提取每个检查项对应的数据。

规则：
1. 逐一检查每个检查项，尝试从照片中找出对应的数值或状态
2. 将实际值与预期结果进行对比，判断该检查项是"正常"还是"异常"
3. 如果照片中无法识别某个检查项的数据，结果标记为"跳过"
4. 只返回 JSON，不要输出任何其他内容
5. 数值提取应精确，保留照片中显示的格式（含单位）
6. 如果预期结果是范围型（如"25±2°C"），实际值在范围内则为正常"""


def build_user_prompt(items: list[dict]) -> str:
    """构建用户提示词。

    Args:
        items: 检查项列表，每项包含 item_name, expected_result
    """
    import json

    items_text = json.dumps(items, ensure_ascii=False, indent=2)
    return f"""请分析上传的设备巡检照片，提取以下检查项的数据：

检查项列表：
{items_text}

请返回一个 JSON 对象，格式如下：
{{{{
  "items": [
    {{{{
      "item_name": "检查项名称（与输入对应）",
      "result": "正常",
      "actual_value": "实际读数值",
      "remark": "分析说明（可选）"
    }}}}
  ]
}}}}

每个检查项的 result 可选值：
- "正常"：实际值与预期结果相符
- "异常"：实际值与预期结果不符
- "跳过"：照片中无法识别该检查项的数据
"""


# ═══════════ 结果修正提示词 ═══════════

CORRECTION_SYSTEM_PROMPT = (
    "你是一个巡检结果修正助手，服务于原料药生产企业的设备巡检工作。\n"
    "\n"
    "用户已完成一轮 AI 巡检分析，现在想通过自然语言对部分检查项的结果进行修改。\n"
    "\n"
    "你的任务是根据用户的修改描述，更新对应的检查项结果。\n"
    "\n"
    "规则：\n"
    "1. 只修改用户明确提到的检查项，未提到的保持原样\n"
    '2. result 只允许三个值："正常"、"异常"、"跳过"\n'
    "3. 如果用户修改了 result 但没有提供 actual_value，保留原来的 actual_value\n"
    "4. 如果用户提供了新的实际值，更新 actual_value\n"
    "5. remark 可根据用户的描述适当更新\n"
    "6. 必须返回所有检查项（包括未修改的），不能遗漏\n"
    "7. 只返回 JSON，不要输出任何其他内容"
)


def build_correction_user_prompt(
    current_results: list[dict], user_text: str
) -> str:
    """构建修正用户提示词。

    Args:
        current_results: 当前检查结果列表（含 template_item_id）
        user_text: 用户发送的自然语言修改文本
    """
    import json

    items_text = json.dumps(
        [
            {
                "template_item_id": r["template_item_id"],
                "item_name": r["item_name"],
                "result": r["result"],
                "actual_value": r.get("actual_value"),
                "remark": r.get("remark"),
            }
            for r in current_results
        ],
        ensure_ascii=False,
        indent=2,
    )

    return f"""当前巡检结果如下：
{items_text}

用户希望对部分结果进行修改，修改说明：
{user_text}

请返回更新后的完整结果 JSON，格式如下：
{{{{
  "items": [
    {{{{
      "template_item_id": "检查项ID（保持不变）",
      "item_name": "检查项名称（保持不变）",
      "result": "正常/异常/跳过",
      "actual_value": "实际值（可为null）",
      "remark": "备注（可为null）"
    }}}}
  ]
}}}}

注意：必须返回所有检查项，未修改的保持原样。"""
