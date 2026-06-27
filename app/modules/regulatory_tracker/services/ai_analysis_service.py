"""AI 分析服务 - 原料药企业法规影响评估 V2。"""

import json
import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.llm import llm_client, LLMError
from app.modules.regulatory_tracker import repository as repo
from app.modules.regulatory_tracker.models.regulatory_document import RegulatoryDocument

# 导入 identity model 以解决外键引用问题
from app.platform.identity.models import User  # noqa: F401

logger = logging.getLogger(__name__)


# 影响等级阈值定义
IMPACT_THRESHOLDS = {
    "high": (0.80, 1.00),
    "medium": (0.50, 0.79),
    "low": (0.20, 0.49),
    "none": (0.00, 0.19),
}


def score_to_impact_level(score: float) -> str:
    """将影响评分转换为影响等级。"""
    if score >= 0.80:
        return "high"
    elif score >= 0.50:
        return "medium"
    elif score >= 0.20:
        return "low"
    else:
        return "none"


def build_analysis_prompt(document: RegulatoryDocument) -> list[dict]:
    """构建原料药企业法规影响评估 Prompt。"""
    title = document.title or ""
    classification = document.classification or "未知"
    status_text = document.status_text or "未知"
    
    # 从 raw_data 提取更多信息
    raw_data = document.raw_data or {}
    content_summary = raw_data.get("contentSummary", "") or raw_data.get("summary", "")
    detail_text = raw_data.get("detail_text", "") or ""
    
    # 组合正文内容（限制长度）
    content_text = detail_text[:3000] if detail_text else content_summary[:1500]
    
    prompt = f"""你是一名服务于原料药生产企业的法规事务、质量保证、GMP 和注册申报专家。请分析以下法规文档，评估其对原料药企业的影响。

## 文档信息
- 标题: {title}
- 分类: {classification}
- 状态: {status_text}
- 内容: {content_text if content_text else "无详细内容"}

## 分析目标

你的任务不是简单摘要，而是判断该法规对原料药企业在以下**10 个生命周期环节**的影响：

1. 药品研发
2. 工艺开发
3. 分析方法
4. 质量标准
5. 稳定性研究
6. 生产管理
7. GMP 管理
8. 注册申报
9. 变更管理
10. 上市后维护

## 影响等级判断规则

**提高影响等级的情况：**
- 涉及原料药（API）
- 涉及药品注册、CTD 资料
- 涉及药学研究、质量研究
- 涉及稳定性研究
- 涉及 GMP、生产管理
- 涉及变更控制
- 指导原则、法规、公告
- ICH 指导原则
- 药典标准

**降低影响等级的情况：**
- 会议新闻、培训通知
- 一般动态、行业资讯
- 与原料药无直接关联
- 仅涉及制剂、临床试验（非原料药相关）

**影响评分标准（0-1）：**
- 0.80-1.00：high，高影响，需要立即评估
- 0.50-0.79：medium，中影响，建议关注并评估
- 0.20-0.49：low，低影响，归档关注
- 0.00-0.19：none，暂无明显影响

## 输出格式

请严格按以下 JSON 格式返回，不要包含其他内容：

{{
  "executive_summary": "一句话结论，概括法规核心内容和对原料药企业的主要影响",
  "regulation_type": "法规类型（如：指导原则、法规、公告、征求意见稿、通知等）",
  "impact_score": 0.85,
  "impact_level": "high|medium|low|none",
  "lifecycle_impacts": [
    {{
      "area": "药品研发",
      "affected": true,
      "reason": "具体原因说明"
    }}
  ],
  "departments": ["注册", "QA", "QC", "研发", "生产", "验证", "供应链"],
  "ctd_sections": ["3.2.S.2", "3.2.S.3", "3.2.S.4", "3.2.S.5", "3.2.S.6", "3.2.S.7"],
  "recommended_actions": [
    "具体建议行动1",
    "具体建议行动2"
  ],
  "notification_required": true,
  "confidence": 0.85,
  "evidence": ["关键词1", "关键词2", "关键词3"]
}}

**字段说明：**
- `executive_summary`: 一句话结论
- `regulation_type`: 法规类型
- `impact_score`: 影响评分（0-1），根据上述标准判断
- `impact_level`: 影响等级（high/medium/low/none），与 impact_score 对应
- `lifecycle_impacts`: 10 个生命周期环节的影响评估，每个环节包含 area（环节名称）、affected（是否受影响）、reason（原因）
- `departments`: 需要关注的部门列表（从以下选择：注册、QA、QC、研发、生产、验证、供应链）
- `ctd_sections`: 可能影响的 CTD 章节（从以下选择：3.2.S.2、3.2.S.3、3.2.S.4、3.2.S.5、3.2.S.6、3.2.S.7）
- `recommended_actions`: 建议采取的具体行动（2-5 条）
- `notification_required`: 是否建议通知相关部门（high/medium 影响通常为 true）
- `confidence`: AI 对该评估的置信度（0-1）
- `evidence`: 从法规标题或正文中提取的关键词或短语，作为判断依据（3-5 个）

**注意事项：**
- 只返回 JSON，不要有其他文字
- 如果法规与原料药无关，impact_score 应低于 0.20，impact_level 为 "none"
- lifecycle_impacts 应包含所有 10 个环节，affected 为 false 时 reason 可为空字符串
- evidence 必须来自法规原文，不要编造"""

    return [
        {"role": "system", "content": "你是专业的药品注册和 GMP 合规专家，专注于化学原料药领域的法规分析。你的分析必须严谨、准确，基于法规原文内容。"},
        {"role": "user", "content": prompt},
    ]


def validate_impact_result(result: dict) -> dict:
    """验证和规范化影响评估结果。"""
    # 验证 impact_level
    valid_levels = {"high", "medium", "low", "none"}
    if result.get("impact_level") not in valid_levels:
        result["impact_level"] = "low"
    
    # 验证 impact_score
    try:
        score = float(result.get("impact_score", 0.5))
        result["impact_score"] = max(0.0, min(1.0, score))
    except (ValueError, TypeError):
        result["impact_score"] = 0.5
    
    # 确保 impact_level 与 impact_score 一致
    expected_level = score_to_impact_level(result["impact_score"])
    if result["impact_level"] != expected_level:
        logger.warning(f"Impact level mismatch: score={result['impact_score']}, level={result['impact_level']}, expected={expected_level}")
        result["impact_level"] = expected_level
    
    # 验证 lifecycle_impacts
    if not isinstance(result.get("lifecycle_impacts"), list):
        result["lifecycle_impacts"] = []
    
    # 验证数组字段
    array_fields = ["departments", "ctd_sections", "recommended_actions", "evidence"]
    for field in array_fields:
        if not isinstance(result.get(field), list):
            result[field] = []
    
    # 验证 confidence
    try:
        confidence = float(result.get("confidence", 0.5))
        result["confidence"] = max(0.0, min(1.0, confidence))
    except (ValueError, TypeError):
        result["confidence"] = 0.5
    
    # 验证 notification_required
    if not isinstance(result.get("notification_required"), bool):
        result["notification_required"] = result.get("impact_level") in ["high", "medium"]
    
    # 确保字符串字段
    for field in ["executive_summary", "regulation_type"]:
        if not isinstance(result.get(field), str):
            result[field] = ""
    
    return result


async def analyze_document(document: RegulatoryDocument) -> dict[str, Any]:
    """使用 AI 分析单个文档的原料药企业影响。

    Args:
        document: 待分析的法规文档

    Returns:
        分析结果字典
    """
    messages = build_analysis_prompt(document)
    
    try:
        result = await llm_client.chat_json(
            messages,
            expected_keys=["executive_summary", "impact_score", "impact_level"],
        )
        
        # 验证和规范化结果
        result = validate_impact_result(result)
        
        return {
            "executive_summary": result.get("executive_summary", ""),
            "regulation_type": result.get("regulation_type", ""),
            "impact_score": result.get("impact_score", 0.5),
            "impact_level": result.get("impact_level", "low"),
            "lifecycle_impacts": result.get("lifecycle_impacts", []),
            "departments": result.get("departments", []),
            "ctd_sections": result.get("ctd_sections", []),
            "recommended_actions": result.get("recommended_actions", []),
            "notification_required": result.get("notification_required", False),
            "confidence": result.get("confidence", 0.5),
            "evidence": result.get("evidence", []),
            "status": "completed",
        }
        
    except LLMError as e:
        logger.error(f"AI 分析文档失败 [{document.document_id}]: {e}")
        return {
            "executive_summary": None,
            "regulation_type": None,
            "impact_score": None,
            "impact_level": None,
            "lifecycle_impacts": None,
            "departments": None,
            "ctd_sections": None,
            "recommended_actions": None,
            "notification_required": None,
            "confidence": None,
            "evidence": None,
            "status": "failed",
            "error": str(e),
        }
    except Exception as e:
        logger.error(f"AI 分析文档异常 [{document.document_id}]: {e}")
        return {
            "executive_summary": None,
            "regulation_type": None,
            "impact_score": None,
            "impact_level": None,
            "lifecycle_impacts": None,
            "departments": None,
            "ctd_sections": None,
            "recommended_actions": None,
            "notification_required": None,
            "confidence": None,
            "evidence": None,
            "status": "failed",
            "error": str(e),
        }


async def analyze_and_update(
    db: AsyncSession,
    document: RegulatoryDocument,
) -> bool:
    """分析文档并更新数据库。

    Args:
        db: 数据库会话
        document: 待分析的文档

    Returns:
        是否成功
    """
    logger.info(f"开始 AI 影响评估: {document.title[:50]}...")
    
    # 标记为分析中
    await repo.update_document(db, document.id, {
        "ai_analysis_status": "pending",
    })
    await db.commit()
    
    # 执行 AI 分析
    result = await analyze_document(document)
    
    # 更新分析结果
    update_data = {
        "ai_analysis_status": result["status"],
        "ai_analyzed_at": datetime.now(timezone.utc),
    }
    
    if result["status"] == "completed":
        # ai_summary: 一句话结论
        update_data["ai_summary"] = result["executive_summary"]
        
        # ai_key_points: 完整结构化结果（JSONB）
        update_data["ai_key_points"] = {
            "regulation_type": result["regulation_type"],
            "impact_level": result["impact_level"],
            "lifecycle_impacts": result["lifecycle_impacts"],
            "departments": result["departments"],
            "ctd_sections": result["ctd_sections"],
            "recommended_actions": result["recommended_actions"],
            "notification_required": result["notification_required"],
            "evidence": result["evidence"],
        }
        
        # ai_relevance_score: 影响评分（0-1）
        update_data["ai_relevance_score"] = result["impact_score"]
    
    await repo.update_document(db, document.id, update_data)
    await db.commit()
    
    logger.info(f"AI 影响评估完成: {document.title[:50]}... (状态: {result['status']}, 影响等级: {result.get('impact_level')}, 评分: {result.get('impact_score')})")
    return result["status"] == "completed"


async def analyze_new_documents(
    db: AsyncSession,
    channel_id: str | None = None,
    limit: int = 10,
) -> dict[str, int]:
    """批量分析新文档。

    Args:
        db: 数据库会话
        channel_id: 可选的栏目 ID 过滤
        limit: 最多分析多少文档

    Returns:
        统计信息 {"analyzed": int, "failed": int, "skipped": int}
    """
    from sqlalchemy import select, and_
    
    # 查询未分析的文档
    stmt = select(RegulatoryDocument).where(
        and_(
            RegulatoryDocument.is_deleted == False,
            RegulatoryDocument.ai_analysis_status == None,
        )
    )
    
    if channel_id:
        stmt = stmt.where(RegulatoryDocument.channel_id == channel_id)
    
    stmt = stmt.order_by(RegulatoryDocument.first_found_at.desc()).limit(limit)
    
    result = await db.execute(stmt)
    documents = result.scalars().all()
    
    stats = {"analyzed": 0, "failed": 0, "skipped": 0}
    
    for doc in documents:
        success = await analyze_and_update(db, doc)
        if success:
            stats["analyzed"] += 1
        else:
            stats["failed"] += 1
    
    logger.info(f"批量分析完成: {stats}")
    return stats
