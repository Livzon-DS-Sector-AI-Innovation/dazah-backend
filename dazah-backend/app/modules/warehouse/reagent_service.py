"""试剂管理 Service

提供试剂/标准品领用台账的业务逻辑，包括 AI 生成领用事由和报废原因。
"""

import logging
import time
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.platform.ai.minimax_util import MinimaxAiUtil, get_ai_util
from app.platform.ai.service import AiLogService

logger = logging.getLogger(__name__)

# AI System Prompt 配置
SYSTEM_PROMPT_REASON = (
    "你是制药QC实验室管理员，按照GMP物料管理规范，"
    "结合试剂用途，生成正式、合规的试剂领用事由，文字简洁专业。"
)

SYSTEM_PROMPT_SCRAP = (
    "根据试剂实际情况，生成符合实验室台账要求的标准报废原因描述，"
    "用语严谨合规。"
)

SYSTEM_PROMPT_ANALYSE = (
    "针对试剂近效期、变质、储存异常等问题，分析潜在原因，"
    "并给出临时处置措施、长期预防管理建议，符合GMP实验室物料管控要求。"
    "用中文输出，条理清晰，分点说明。"
)

# AI 操作类型配置
OPERATE_TYPE_REASON = "试剂领用辅助"
OPERATE_TYPE_SCRAP = "试剂报废辅助"
OPERATE_TYPE_ANALYSE = "试剂异常分析"

# 兜底文案
FALLBACK_MESSAGE = "AI服务暂时不可用，请手动填写"


class ReagentService:
    """试剂管理 Service

    提供试剂相关的业务逻辑，包括 AI 能力调用。
    """

    def __init__(self, session: AsyncSession):
        """初始化试剂服务

        Args:
            session: 数据库会话
        """
        self.session = session
        self.ai_util: Optional[MinimaxAiUtil] = None
        self.ai_log_service = AiLogService(session)

    def _get_ai_util(self) -> MinimaxAiUtil:
        """获取 AI 工具实例（延迟初始化）"""
        if self.ai_util is None:
            try:
                self.ai_util = get_ai_util()
            except ValueError as e:
                logger.warning(f"MiniMax AI 未配置: {e}")
                raise
        return self.ai_util

    async def generate_reason(
        self,
        bill_no: str,
        user_input: str,
        operator: str,
    ) -> dict:
        """AI 生成合规领用事由

        Args:
            bill_no: 领用单据编号
            user_input: 用户补充描述内容
            operator: 当前操作人账号

        Returns:
            包含生成结果的字典

        Raises:
            ValueError: 参数为空时抛出
        """
        # 入参非空校验
        if not bill_no or not bill_no.strip():
            raise ValueError("单据编号不能为空")
        if not user_input or not user_input.strip():
            raise ValueError("用户补充描述内容不能为空")
        if not operator or not operator.strip():
            raise ValueError("操作人账号不能为空")

        start_time = time.time()
        ai_response = None
        error_message = None

        try:
            # 调用 MiniMax AI
            ai_util = self._get_ai_util()
            ai_response = ai_util.chat(
                system_prompt=SYSTEM_PROMPT_REASON,
                user_message=user_input,
            )

            # 保存 AI 交互日志
            latency_ms = int((time.time() - start_time) * 1000)
            await self.ai_log_service.save_ai_log(
                operate_type=OPERATE_TYPE_REASON,
                operator=operator,
                system_prompt=SYSTEM_PROMPT_REASON,
                user_input=user_input,
                ai_response=ai_response,
                bill_no=bill_no,
                latency_ms=latency_ms,
            )

            return {
                "result": ai_response,
                "bill_no": bill_no,
                "operate_type": OPERATE_TYPE_REASON,
            }

        except Exception as e:
            logger.error(f"AI 生成领用事由失败: {e}")

            # 保存错误日志
            latency_ms = int((time.time() - start_time) * 1000)
            try:
                await self.ai_log_service.save_ai_log(
                    operate_type=OPERATE_TYPE_REASON,
                    operator=operator,
                    system_prompt=SYSTEM_PROMPT_REASON,
                    user_input=user_input,
                    error_message=str(e),
                    bill_no=bill_no,
                    latency_ms=latency_ms,
                )
            except Exception as log_error:
                logger.error(f"AI 日志保存失败: {log_error}")

            # 返回兜底文案
            return {
                "result": FALLBACK_MESSAGE,
                "bill_no": bill_no,
                "operate_type": OPERATE_TYPE_REASON,
            }

    async def generate_scrap(
        self,
        bill_no: str,
        user_input: str,
        operator: str,
    ) -> dict:
        """AI 生成标准报废原因

        Args:
            bill_no: 报废单据编号
            user_input: 用户补充描述内容
            operator: 当前操作人账号

        Returns:
            包含生成结果的字典

        Raises:
            ValueError: 参数为空时抛出
        """
        # 入参非空校验
        if not bill_no or not bill_no.strip():
            raise ValueError("单据编号不能为空")
        if not user_input or not user_input.strip():
            raise ValueError("用户补充描述内容不能为空")
        if not operator or not operator.strip():
            raise ValueError("操作人账号不能为空")

        start_time = time.time()
        ai_response = None
        error_message = None

        try:
            # 调用 MiniMax AI
            ai_util = self._get_ai_util()
            ai_response = ai_util.chat(
                system_prompt=SYSTEM_PROMPT_SCRAP,
                user_message=user_input,
            )

            # 保存 AI 交互日志
            latency_ms = int((time.time() - start_time) * 1000)
            await self.ai_log_service.save_ai_log(
                operate_type=OPERATE_TYPE_SCRAP,
                operator=operator,
                system_prompt=SYSTEM_PROMPT_SCRAP,
                user_input=user_input,
                ai_response=ai_response,
                bill_no=bill_no,
                latency_ms=latency_ms,
            )

            return {
                "result": ai_response,
                "bill_no": bill_no,
                "operate_type": OPERATE_TYPE_SCRAP,
            }

        except Exception as e:
            logger.error(f"AI 生成报废原因失败: {e}")

            # 保存错误日志
            latency_ms = int((time.time() - start_time) * 1000)
            try:
                await self.ai_log_service.save_ai_log(
                    operate_type=OPERATE_TYPE_SCRAP,
                    operator=operator,
                    system_prompt=SYSTEM_PROMPT_SCRAP,
                    user_input=user_input,
                    error_message=str(e),
                    bill_no=bill_no,
                    latency_ms=latency_ms,
                )
            except Exception as log_error:
                logger.error(f"AI 日志保存失败: {log_error}")

            # 返回兜底文案
            return {
                "result": FALLBACK_MESSAGE,
                "bill_no": bill_no,
                "operate_type": OPERATE_TYPE_SCRAP,
            }

    async def generate_analyse(
        self,
        bill_no: str,
        reagent_name: str,
        problem_description: str,
        storage_conditions: str,
        operator: str,
    ) -> dict:
        """AI 试剂异常分析

        Args:
            bill_no: 单据编号
            reagent_name: 试剂名称
            problem_description: 问题描述
            storage_conditions: 储存条件
            operator: 当前操作人账号

        Returns:
            包含分析结果的字典

        Raises:
            ValueError: 参数为空时抛出
        """
        # 入参非空校验
        if not bill_no or not bill_no.strip():
            raise ValueError("单据编号不能为空")
        if not reagent_name or not reagent_name.strip():
            raise ValueError("试剂名称不能为空")
        if not problem_description or not problem_description.strip():
            raise ValueError("问题描述不能为空")
        if not operator or not operator.strip():
            raise ValueError("操作人账号不能为空")

        # 构建用户输入
        user_message = (
            f"试剂名称：{reagent_name}\n"
            f"问题描述：{problem_description}\n"
            f"储存条件：{storage_conditions or '未知'}"
        )

        start_time = time.time()

        try:
            # 调用 MiniMax AI
            ai_util = self._get_ai_util()
            ai_response = ai_util.chat(
                system_prompt=SYSTEM_PROMPT_ANALYSE,
                user_message=user_message,
            )

            # 保存 AI 交互日志
            latency_ms = int((time.time() - start_time) * 1000)
            await self.ai_log_service.save_ai_log(
                operate_type=OPERATE_TYPE_ANALYSE,
                operator=operator,
                system_prompt=SYSTEM_PROMPT_ANALYSE,
                user_input=user_message,
                ai_response=ai_response,
                bill_no=bill_no,
                latency_ms=latency_ms,
            )

            return {
                "result": ai_response,
                "bill_no": bill_no,
                "operate_type": OPERATE_TYPE_ANALYSE,
            }

        except Exception as e:
            logger.error(f"AI 试剂异常分析失败: {e}")

            # 保存错误日志
            latency_ms = int((time.time() - start_time) * 1000)
            try:
                await self.ai_log_service.save_ai_log(
                    operate_type=OPERATE_TYPE_ANALYSE,
                    operator=operator,
                    system_prompt=SYSTEM_PROMPT_ANALYSE,
                    user_input=user_message,
                    error_message=str(e),
                    bill_no=bill_no,
                    latency_ms=latency_ms,
                )
            except Exception as log_error:
                logger.error(f"AI 日志保存失败: {log_error}")

            # 返回兜底文案
            return {
                "result": FALLBACK_MESSAGE,
                "bill_no": bill_no,
                "operate_type": OPERATE_TYPE_ANALYSE,
            }