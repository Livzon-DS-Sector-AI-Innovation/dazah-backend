"""巡检飞书交互服务 — 处理从飞书接收的巡检照片和后续确认/修改/提交。

接收飞书图片消息 → 下载 → AI 分析 → 保存照片 → 回复结果 → 等待确认提交。
"""

import base64
import json
import logging
import os
import uuid
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import async_session_factory
from app.core.exceptions import AppException
from app.modules.equipment.feishu.notification import send_user_card
from app.modules.equipment.models.inspection import InspectionPhoto, InspectionTask
from app.modules.equipment.service.inspection_session import (
    clear_session,
    get_session,
    save_session,
    update_results,
)

logger = logging.getLogger(__name__)

_UPLOAD_DIR = "uploads/inspection"
os.makedirs(_UPLOAD_DIR, exist_ok=True)


async def process_feishu_image(
    *,
    user_id: str,
    open_id: str,
    message_id: str,
    image_key: str,
    chat_id: str,
    chat_type: str,
) -> None:
    """处理从飞书收到的巡检照片。

    流程：查用户 → 查任务 → 下载图片 → AI 分析 → 保存照片 → 回复结果。
    """
    if not user_id:
        logger.warning("消息缺少 sender user_id，忽略")
        return

    async with async_session_factory() as db:
        # 1. 根据 user_id 查找用户（租户级标识，跨应用通用）
        user = await _find_user_by_user_id(db, user_id)
        if not user:
            logger.warning("飞书用户未匹配系统账号: open_id=%s", open_id)
            await _reply_text(open_id, "未找到您的系统账号，请先在系统中完成飞书绑定。")
            return

        # 2. 查找该用户正在执行的巡检任务
        task = await _find_active_task(db, user.id)
        if not task:
            await _reply_text(
                open_id, "当前没有执行中的巡检任务。\n请先在系统中开始巡检。"
            )
            return

        # 3. 确定设备 ID（多设备模式下找第一个未提交的）
        equipment_id = await _resolve_equipment_id(db, task)
        if not equipment_id:
            await _reply_text(
                open_id,
                "该任务所有设备均已提交巡检结果。\n"
                "如需修改请在系统中操作。",
            )
            return

        # 3b. 查询设备名称
        equipment_name = await _get_equipment_name(db, equipment_id)

        # 4. 下载图片
        image_bytes, mime_type = await _download_image(message_id, image_key)
        if not image_bytes:
            await _reply_text(open_id, "图片下载失败，请重新发送。")
            return

        # 5. 保存照片
        photo = await _save_photo(db, task.id, equipment_id, image_bytes)
        logger.info("巡检照片已保存: task=%s, photo=%s", task.task_no, photo.id)

        # 6. AI 分析
        try:
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")
            from app.modules.equipment.service.ai.service import (
                analyze_inspection_photo,
            )

            results = await analyze_inspection_photo(
                db=db,
                task_id=task.id,
                equipment_id=equipment_id,
                image_base64=image_b64,
                image_mime_type=mime_type or "image/jpeg",
            )
        except Exception as e:
            logger.exception("AI 分析失败: task=%s", task.task_no)
            await _reply_text(
                open_id, f"AI 分析失败：{e}\n照片已保存，请在系统中手动录入检查结果。"
            )
            return

        # 7. 发送结果卡片
        await _send_result_card(
            open_id, task, results, equipment_name=equipment_name,
        )

        # 8. 保存会话，等待用户确认/修改
        await save_session(
            open_id,
            task_id=str(task.id),
            equipment_id=str(equipment_id),
            task_no=task.task_no,
            equipment_name=equipment_name,
            results=results,
        )


async def _find_user_by_user_id(
    db: AsyncSession, user_id: str
) -> Any | None:
    """根据飞书 user_id（租户级）查找系统用户。"""
    from app.platform.identity.models import User

    logger.info("查找用户: feishu_user_id=%s", user_id)
    result = await db.execute(
        select(User).where(
            User.feishu_user_id == user_id,
            User.is_deleted == False,  # noqa: E712
        )
    )
    return result.scalar_one_or_none()


async def _find_active_task(
    db: AsyncSession, user_id: uuid.UUID
) -> InspectionTask | None:
    """查找用户正在执行的最新巡检任务。"""
    result = await db.execute(
        select(InspectionTask)
        .options(
            selectinload(InspectionTask.equipment),
            selectinload(InspectionTask.template),
        )
        .where(
            InspectionTask.assigned_to == user_id,
            InspectionTask.status == "执行中",
            InspectionTask.is_deleted == False,  # noqa: E712
        )
        .order_by(InspectionTask.started_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def _resolve_equipment_id(
    db: AsyncSession, task: InspectionTask,
) -> uuid.UUID | None:
    """从巡检任务中确定待巡检的设备 ID。

    单设备模式直接返回；多设备模式返回第一个尚未提交记录的设备。
    """
    # 单设备模式
    if task.equipment_id:
        return task.equipment_id
    # 多设备模式：找第一个未提交的
    if task.equipment_ids:
        from app.modules.equipment.models.inspection_template import (
            InspectionRecord,
        )

        # 查询已有记录的设备 ID
        result = await db.execute(
            select(InspectionRecord.equipment_id)
            .where(
                InspectionRecord.task_id == task.id,
                InspectionRecord.is_deleted == False,  # noqa: E712
            )
            .distinct()
        )
        submitted_ids = {row for row in result.scalars().all()}

        for eid in task.equipment_ids:
            eq_id = uuid.UUID(eid) if isinstance(eid, str) else eid
            if eq_id not in submitted_ids:
                return eq_id

        # 所有设备都已提交
        return None
    return None


async def _get_equipment_name(
    db: AsyncSession, equipment_id: uuid.UUID
) -> str:
    """根据设备 ID 查询设备名称。"""
    from app.modules.equipment.models.equipment import Equipment

    result = await db.execute(
        select(Equipment.name).where(Equipment.id == equipment_id)
    )
    return result.scalar_one_or_none() or "未知设备"


async def _download_image(
    message_id: str, image_key: str
) -> tuple[bytes | None, str | None]:
    """从飞书下载消息中的图片（使用设备机器人凭证）。

    Returns:
        (图片字节数据, MIME类型)，失败返回 (None, None)
    """
    from lark_oapi.api.im.v1.model.get_message_resource_request import (
        GetMessageResourceRequest,
    )

    from app.modules.equipment.feishu.client import (
        get_equipment_feishu_client,
        get_equipment_tenant_token,
    )

    client = await get_equipment_feishu_client()
    token = await get_equipment_tenant_token(client)

    req = (
        GetMessageResourceRequest.builder()
        .message_id(message_id)
        .file_key(image_key)
        .type("image")
        .build()
    )
    req.headers["Authorization"] = f"Bearer {token}"

    try:
        resp = await client.im.v1.message_resource.aget(req)
        if resp.code == 0 and resp.file:
            image_bytes = resp.file.read()
            logger.info(
                "图片下载成功: message_id=%s, size=%d bytes",
                message_id, len(image_bytes),
            )
            # 飞书图片默认 JPEG
            return image_bytes, "image/jpeg"
        else:
            logger.error(
                "图片下载失败: code=%s, msg=%s", resp.code, resp.msg
            )
            return None, None
    except Exception:
        logger.exception(
            "图片下载异常: message_id=%s, image_key=%s",
            message_id, image_key,
        )
        return None, None


async def _save_photo(
    db: AsyncSession,
    task_id: uuid.UUID,
    equipment_id: uuid.UUID,
    image_bytes: bytes,
) -> InspectionPhoto:
    """保存巡检照片到文件和数据库。"""
    filename = f"{uuid.uuid4()}_feishu.jpg"
    file_path = os.path.normpath(os.path.join(_UPLOAD_DIR, filename))

    with open(file_path, "wb") as f:
        f.write(image_bytes)

    photo = InspectionPhoto(
        task_id=task_id,
        equipment_id=equipment_id,
        file_name=filename,
        file_path=file_path,
        file_size=len(image_bytes),
    )
    db.add(photo)
    await db.commit()

    # eager re-fetch to avoid MissingGreenlet
    result = await db.execute(
        select(InspectionPhoto).where(InspectionPhoto.id == photo.id)
    )
    return result.scalar_one()


async def _send_result_card(
    open_id: str,
    task: InspectionTask,
    results: list[dict],
    *,
    equipment_name: str,
    is_correction: bool = False,
) -> None:
    """构建并发送 AI 分析结果卡片。"""
    title_prefix = "✏️ 修改后 - " if is_correction else ""
    content = _build_result_card_content(task, results, equipment_name)

    await send_user_card(
        open_id=open_id,
        title=f"{title_prefix}🔍 巡检AI分析 - {equipment_name}",
        content=content,
        receive_id_type="open_id",
    )


async def _send_session_result_card(
    open_id: str,
    session: dict,
    *,
    is_correction: bool = False,
) -> None:
    """从会话数据构建并发送结果卡片（无需 ORM 对象）。"""
    title_prefix = "✏️ 修改后 - " if is_correction else ""
    equipment_name = session.get("equipment_name", "未知设备")

    content = _build_result_card_content_from_session(session)

    await send_user_card(
        open_id=open_id,
        title=f"{title_prefix}🔍 巡检AI分析 - {equipment_name}",
        content=content,
        receive_id_type="open_id",
    )


def _build_result_card_content(
    task: InspectionTask, results: list[dict], equipment_name: str
) -> str:
    """构建结果卡片的 Markdown 内容。"""
    return _build_result_card_content_from_session(
        {
            "task_no": task.task_no,
            "equipment_name": equipment_name,
            "results": results,
        }
    )


def _build_result_card_content_from_session(session: dict) -> str:
    """从会话数据构建结果卡片的 Markdown 内容。"""
    task_no = session.get("task_no", "")
    equipment_name = session.get("equipment_name", "未知设备")
    results = session.get("results", [])

    normal_count = sum(1 for r in results if r["result"] == "正常")
    abnormal_count = sum(1 for r in results if r["result"] == "异常")
    skip_count = sum(1 for r in results if r["result"] == "跳过")

    lines = [
        f"**任务：**{task_no}",
        f"**设备：**{equipment_name}",
        "",
        "---",
        "**📋 AI 分析结果：**",
        "",
    ]

    for r in results:
        if r["result"] == "正常":
            icon = "✅"
        elif r["result"] == "异常":
            icon = "⚠️"
        else:
            icon = "⏭️"
        value = f" → {r['actual_value']}" if r.get("actual_value") else ""
        remark = f"（{r['remark']}）" if r.get("remark") else ""
        lines.append(f"{icon} **{r['item_name']}**：{r['result']}{value}{remark}")

    lines.append("")
    lines.append("---")
    lines.append(
        f"**汇总：** ✅ 正常 {normal_count} 项 | "
        f"⚠️ 异常 {abnormal_count} 项 | "
        f"⏭️ 跳过 {skip_count} 项"
    )
    lines.append("")
    lines.append(
        "> 📌 回复 **提交** 保存结果 | 发送文字修改内容 | 回复 **取消** 放弃"
    )

    return "\n".join(lines)


# ═══════════ 确认/修改/提交流程 ═══════════


async def process_correction(open_id: str, user_text: str) -> None:
    """处理用户对巡检结果的修改请求。

    将用户的自然语言修改描述发送给 AI 解析，更新会话中的结果，
    并发送修改后的结果卡片供用户再次确认。
    """
    session = await get_session(open_id)
    if session is None:
        await _reply_text(open_id, "当前没有待修改的巡检结果。\n请先发送巡检照片。")
        return

    current_results = session.get("results", [])
    if not current_results:
        await _reply_text(open_id, "会话中没有检查结果数据，请重新发送巡检照片。")
        return

    # 调用 AI 解析修改
    from app.modules.equipment.service.ai.client import AIAnalysisError, QwenClient
    from app.modules.equipment.service.ai.prompts import (
        CORRECTION_SYSTEM_PROMPT,
        build_correction_user_prompt,
    )

    client = QwenClient()
    try:
        user_prompt = build_correction_user_prompt(current_results, user_text)
        raw_response = await client.parse_correction(
            system_prompt=CORRECTION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )
    except AIAnalysisError as e:
        logger.warning("AI 修正解析失败: open_id=%s, error=%s", open_id, e)
        await _reply_text(
            open_id,
            f"无法理解您的修改：{e.message}\n"
            "请换一种方式描述，或发送新照片重新分析。",
        )
        return
    except httpx.RequestError as e:
        logger.exception("AI 修正请求失败: open_id=%s", open_id)
        await _reply_text(open_id, f"AI 服务暂时不可用：{e}\n请稍后再试。")
        return
    finally:
        await client.close()

    # 解析 AI 响应
    try:
        parsed = json.loads(raw_response)
    except json.JSONDecodeError:
        logger.warning("AI 修正返回非 JSON: open_id=%s", open_id)
        await _reply_text(open_id, "无法理解您的修改，请换一种方式描述。")
        return

    ai_items = parsed.get("items", [])
    if not isinstance(ai_items, list) or len(ai_items) == 0:
        await _reply_text(open_id, "无法理解您的修改，请换一种方式描述。")
        return

    # 将 AI 返回的结果按 template_item_id 映射回当前结果
    ai_map: dict[str, dict] = {}
    for item in ai_items:
        tid = item.get("template_item_id")
        if tid:
            ai_map[tid] = item

    updated_results: list[dict] = []
    for r in current_results:
        tid = r["template_item_id"]
        if tid in ai_map:
            ai_item = ai_map[tid]
            result_value = ai_item.get("result", r["result"])
            if result_value not in ("正常", "异常", "跳过"):
                result_value = r["result"]
            updated_results.append({
                "template_item_id": tid,
                "item_name": r["item_name"],
                "expected_result": r.get("expected_result"),
                "result": result_value,
                "actual_value": ai_item.get("actual_value") or None,
                "remark": ai_item.get("remark") or None,
            })
        else:
            # AI 未返回该项，保持原样
            updated_results.append(r)

    # 更新会话
    await update_results(open_id, updated_results)

    # 发送修改后的结果卡片
    session["results"] = updated_results
    await _send_session_result_card(open_id, session, is_correction=True)


async def submit_pending_results(open_id: str) -> None:
    """提交用户确认的巡检结果。

    从会话中读取待确认结果，调用 submit_equipment_check 写入数据库，
    成功后清除会话。
    """
    session = await get_session(open_id)
    if session is None:
        await _reply_text(open_id, "当前没有待提交的巡检结果。\n请先发送巡检照片。")
        return

    task_id = session.get("task_id")
    equipment_id = session.get("equipment_id")
    results = session.get("results", [])
    task_no = session.get("task_no", "")
    equipment_name = session.get("equipment_name", "未知设备")

    if not task_id or not equipment_id or not results:
        await _reply_text(open_id, "会话数据不完整，请重新发送巡检照片。")
        await clear_session(open_id)
        return

    # 构建 records 并调用现有提交逻辑
    records = [
        {
            "template_item_id": r["template_item_id"],
            "result": r["result"],
            "actual_value": r.get("actual_value"),
            "remark": r.get("remark"),
        }
        for r in results
    ]

    try:
        async with async_session_factory() as db:
            from app.modules.equipment.service.inspection import (
                complete_task,
                submit_equipment_check,
            )

            await submit_equipment_check(
                db=db,
                task_id=uuid.UUID(task_id),
                equipment_id=uuid.UUID(equipment_id),
                records=records,
            )

            # 查询任务，检查是否所有设备都已提交
            task_result = await db.execute(
                select(InspectionTask).where(
                    InspectionTask.id == uuid.UUID(task_id),
                )
            )
            task_obj = task_result.scalar_one()

            task_completed = False
            overall_result = ""
            remaining = 0
            if task_obj.equipment_ids:
                from app.modules.equipment.models.inspection_template import (
                    InspectionRecord,
                )

                rec_result = await db.execute(
                    select(InspectionRecord.equipment_id)
                    .where(
                        InspectionRecord.task_id == uuid.UUID(task_id),
                        InspectionRecord.is_deleted == False,  # noqa: E712
                    )
                    .distinct()
                )
                submitted_ids = {row for row in rec_result.scalars().all()}
                all_ids = set()
                for eid in task_obj.equipment_ids:
                    eq_id = uuid.UUID(eid) if isinstance(eid, str) else eid
                    all_ids.add(eq_id)

                remaining = len(all_ids - submitted_ids)
                if remaining == 0:
                    completed = await complete_task(
                        db, uuid.UUID(task_id),
                    )
                    task_completed = True
                    overall_result = completed.overall_result or ""

            await db.commit()
    except AppException as e:
        logger.warning(
            "巡检结果提交失败: open_id=%s, task=%s, error=%s",
            open_id, task_no, e.message,
        )
        await _reply_text(open_id, f"提交失败：{e.message}")
        return
    except Exception:
        logger.exception("巡检结果提交异常: open_id=%s, task=%s", open_id, task_no)
        await _reply_text(open_id, "提交时发生异常，请稍后重试。")
        return

    # 成功 → 清除会话并发送确认卡片
    await clear_session(open_id)

    record_count = len(records)

    # 统计本次提交的异常项
    abnormal_items = [r for r in results if r["result"] == "异常"]

    if task_completed:
        # 所有设备已提交，任务已完成
        result_icon = "⚠️" if overall_result == "异常" else "✅"
        lines = [
            f"**任务：**{task_no}",
            f"**设备：**{equipment_name}",
            f"**提交项数：**{record_count} 项",
            "",
            f"**{result_icon} 任务已完成 — 总体结果：{overall_result}**",
        ]
        if abnormal_items:
            lines.append("")
            lines.append("**异常项：**")
            for item in abnormal_items:
                value = f" → {item['actual_value']}" if item.get("actual_value") else ""
                lines.append(f"⚠️ {item['item_name']}{value}")
    else:
        # 还有设备未提交
        lines = [
            f"**任务：**{task_no}",
            f"**设备：**{equipment_name}",
            f"**提交项数：**{record_count} 项",
        ]
        if abnormal_items:
            lines.append("")
            lines.append("**本次异常项：**")
            for item in abnormal_items:
                value = f" → {item['actual_value']}" if item.get("actual_value") else ""
                lines.append(f"⚠️ {item['item_name']}{value}")
        if remaining > 0:
            lines.append("")
            lines.append(f"> 还剩 {remaining} 台设备未巡检，请继续发送照片。")
        else:
            lines.append("")
            lines.append("> 结果已保存，可在系统中查看详情。")

    await send_user_card(
        open_id=open_id,
        title="✅ 巡检结果已提交",
        content="\n".join(lines),
        receive_id_type="open_id",
    )


async def cancel_pending_session(open_id: str) -> None:
    """取消当前待确认的巡检结果。"""
    session = await get_session(open_id)
    if session is None:
        await _reply_text(open_id, "当前没有待取消的巡检结果。")
        return

    await clear_session(open_id)
    task_no = session.get("task_no", "")
    await _reply_text(
        open_id,
        f"已取消任务 {task_no} 的巡检结果。\n可重新发送照片进行分析。",
    )


async def _reply_text(open_id: str, text: str) -> None:
    """发送纯文本提示卡片。"""
    await send_user_card(
        open_id=open_id,
        title="💬 巡检助手",
        content=text,
        receive_id_type="open_id",
    )


