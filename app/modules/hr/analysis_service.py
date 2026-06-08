"""HR turnover analysis service."""

from collections import Counter
from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.hr.analysis_schemas import (
    AiSuggestion,
    TurnoverAnalysisResponse,
    TurnoverMetrics,
    TurnoverRawData,
)
from app.modules.hr.models import DepartureRecord, OnboardingRecord
from app.platform.ai.service import AiChatService


_TURNOVER_SYSTEM_PROMPT = """你是一位人力资源数据分析顾问，擅长从人员流动数据中发现管理问题并提供针对性建议。

【任务要求】
请用1段话总结人员流动现状，然后给出2条管理建议。

【输出格式】
现状分析：[一段概括性描述，包含统计周期、净增减人数、主要离职原因]

建议1：[一句话行动建议，30字以内]
依据1：[一句话数据支撑，引用具体数字]

建议2：[一句话行动建议，30字以内]
依据2：[一句话数据支撑，引用具体数字]

请严格按上述格式输出，不要添加其他内容。"""


class TurnoverAnalysisService:
    """Service for analyzing HR turnover data and generating AI insights."""

    def __init__(self, session: AsyncSession, ai_service: AiChatService) -> None:
        self.session = session
        self.ai_service = ai_service

    async def analyze(self) -> TurnoverAnalysisResponse:
        """Run full turnover analysis: fetch data, compute metrics, generate AI report."""
        end_date = date.today()
        start_date = end_date - timedelta(days=180)

        raw_data_dict = await self._fetch_all_data(start_date, end_date)
        raw_data_dict["period_start"] = start_date
        raw_data_dict["period_end"] = end_date

        metrics = self._calculate_metrics(raw_data_dict)
        ai_result = await self._generate_ai_analysis(raw_data_dict, metrics)

        raw_data = TurnoverRawData(
            period_start=start_date,
            period_end=end_date,
            onboarding_count=raw_data_dict["onboarding_count"],
            onboarding_by_department=raw_data_dict["onboarding_by_department"],
            onboarding_by_job_category=raw_data_dict["onboarding_by_job_category"],
            onboarding_by_education=raw_data_dict["onboarding_by_education"],
            departure_count=raw_data_dict["departure_count"],
            departure_by_reason=raw_data_dict["departure_by_reason"],
            departure_by_department=raw_data_dict["departure_by_department"],
            departure_by_job_category=raw_data_dict["departure_by_job_category"],
            current_headcount=raw_data_dict["current_headcount"],
        )

        return TurnoverAnalysisResponse(
            raw_data=raw_data,
            metrics=metrics,
            ai_summary=ai_result["summary"],
            ai_suggestions=ai_result["suggestions"],
        )

    async def _fetch_all_data(self, start_date: date, end_date: date) -> dict:
        """Fetch onboarding, departure and headcount data."""
        onboarding_data = await self._fetch_onboarding_data(start_date, end_date)
        departure_data = await self._fetch_departure_data(start_date, end_date)
        headcount = await self._fetch_current_headcount()

        return {
            **onboarding_data,
            **departure_data,
            "current_headcount": headcount,
        }

    async def _fetch_onboarding_data(self, start_date: date, end_date: date) -> dict:
        """Fetch onboarding records within the period."""
        total_stmt = (
            select(func.count())
            .select_from(OnboardingRecord)
            .where(
                OnboardingRecord.hire_date >= start_date,
                OnboardingRecord.hire_date <= end_date,
                OnboardingRecord.is_deleted.is_(False),
            )
        )
        total_result = await self.session.execute(total_stmt)
        total = total_result.scalar() or 0

        dept_stmt = (
            select(OnboardingRecord.department, func.count())
            .where(
                OnboardingRecord.hire_date >= start_date,
                OnboardingRecord.hire_date <= end_date,
                OnboardingRecord.is_deleted.is_(False),
            )
            .group_by(OnboardingRecord.department)
        )
        dept_result = await self.session.execute(dept_stmt)
        by_department = {row[0]: row[1] for row in dept_result.all() if row[0]}

        jc_stmt = (
            select(OnboardingRecord.job_category, func.count())
            .where(
                OnboardingRecord.hire_date >= start_date,
                OnboardingRecord.hire_date <= end_date,
                OnboardingRecord.is_deleted.is_(False),
            )
            .group_by(OnboardingRecord.job_category)
        )
        jc_result = await self.session.execute(jc_stmt)
        by_job_category = {row[0]: row[1] for row in jc_result.all() if row[0]}

        edu_stmt = (
            select(OnboardingRecord.education, func.count())
            .where(
                OnboardingRecord.hire_date >= start_date,
                OnboardingRecord.hire_date <= end_date,
                OnboardingRecord.is_deleted.is_(False),
            )
            .group_by(OnboardingRecord.education)
        )
        edu_result = await self.session.execute(edu_stmt)
        by_education = {row[0]: row[1] for row in edu_result.all() if row[0]}

        return {
            "onboarding_count": total,
            "onboarding_by_department": by_department,
            "onboarding_by_job_category": by_job_category,
            "onboarding_by_education": by_education,
        }

    async def _fetch_departure_data(self, start_date: date, end_date: date) -> dict:
        """Fetch departure records within the period."""
        total_stmt = (
            select(func.count())
            .select_from(DepartureRecord)
            .where(
                DepartureRecord.offboarding_date >= start_date,
                DepartureRecord.offboarding_date <= end_date,
                DepartureRecord.is_deleted.is_(False),
            )
        )
        total_result = await self.session.execute(total_stmt)
        total = total_result.scalar() or 0

        dept_stmt = (
            select(DepartureRecord.department, func.count())
            .where(
                DepartureRecord.offboarding_date >= start_date,
                DepartureRecord.offboarding_date <= end_date,
                DepartureRecord.is_deleted.is_(False),
            )
            .group_by(DepartureRecord.department)
        )
        dept_result = await self.session.execute(dept_stmt)
        by_department = {row[0]: row[1] for row in dept_result.all() if row[0]}

        jc_stmt = (
            select(DepartureRecord.job_category, func.count())
            .where(
                DepartureRecord.offboarding_date >= start_date,
                DepartureRecord.offboarding_date <= end_date,
                DepartureRecord.is_deleted.is_(False),
            )
            .group_by(DepartureRecord.job_category)
        )
        jc_result = await self.session.execute(jc_stmt)
        by_job_category = {row[0]: row[1] for row in jc_result.all() if row[0]}

        reason_stmt = (
            select(
                DepartureRecord.offboarding_reason,
                DepartureRecord.offboarding_reason_2,
            )
            .where(
                DepartureRecord.offboarding_date >= start_date,
                DepartureRecord.offboarding_date <= end_date,
                DepartureRecord.is_deleted.is_(False),
            )
        )
        reason_result = await self.session.execute(reason_stmt)
        reason_counter: Counter[str] = Counter()
        for row in reason_result.all():
            if row[0]:
                reason_counter.update(row[0])
            if row[1]:
                reason_counter.update(row[1])

        return {
            "departure_count": total,
            "departure_by_reason": dict(reason_counter),
            "departure_by_department": by_department,
            "departure_by_job_category": by_job_category,
        }

    async def _fetch_current_headcount(self) -> int:
        """Count current employed staff from onboarding records."""
        stmt = (
            select(func.count())
            .select_from(OnboardingRecord)
            .where(
                OnboardingRecord.is_employed == "是",
                OnboardingRecord.is_deleted.is_(False),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    @staticmethod
    def _calculate_metrics(raw_data: dict) -> TurnoverMetrics:
        """Calculate turnover metrics from raw data."""
        onboarding_count = raw_data["onboarding_count"]
        departure_count = raw_data["departure_count"]
        current_headcount = raw_data["current_headcount"]

        net_change = onboarding_count - departure_count
        initial_headcount = current_headcount - net_change

        if initial_headcount <= 0:
            initial_headcount = 0
            turnover_rate = 0.0
        else:
            turnover_rate = round(departure_count / initial_headcount * 100, 2)

        return TurnoverMetrics(
            net_change=net_change,
            initial_headcount=initial_headcount,
            turnover_rate=turnover_rate,
        )

    async def _generate_ai_analysis(
        self, raw_data: dict, metrics: TurnoverMetrics
    ) -> dict:
        """Generate AI analysis report."""
        start = raw_data.get("period_start")
        end = raw_data.get("period_end")

        reasons = raw_data.get("departure_by_reason", {})
        reason_str = (
            ", ".join(f"{k}:{v}人" for k, v in reasons.items()) if reasons else "无"
        )

        user_prompt = (
            f"统计周期：{start} 至 {end}\n"
            f"老厂入职人数：{raw_data['onboarding_count']} 人\n"
            f"老厂离职人数：{raw_data['departure_count']} 人，"
            f"离职原因分布：{reason_str}\n"
            f"当前在职：老厂{raw_data['current_headcount']}人\n"
            f"净增减人数：{metrics.net_change}人\n"
            f"人员流失率：{metrics.turnover_rate}%"
        )

        messages = [{"role": "user", "content": user_prompt}]

        try:
            content_parts = []
            async for chunk in self.ai_service.stream_chat(
                messages=messages,
                system_prompt=_TURNOVER_SYSTEM_PROMPT,
            ):
                if chunk.get("type") == "content":
                    content_parts.append(chunk.get("text", ""))

            full_text = "".join(content_parts)
            return TurnoverAnalysisService._parse_ai_response(full_text)

        except Exception:
            return {
                "summary": (
                    f"统计周期内老厂入职{raw_data['onboarding_count']}人，"
                    f"离职{raw_data['departure_count']}人，"
                    f"净增减{metrics.net_change}人，"
                    f"人员流失率{metrics.turnover_rate}%。"
                ),
                "suggestions": [],
            }

    @staticmethod
    def _parse_ai_response(text: str) -> dict:
        """Parse AI text response into structured data."""
        text = text.strip()
        summary = ""
        suggestions: list[AiSuggestion] = []

        if "现状分析：" in text:
            summary_start = text.find("现状分析：") + len("现状分析：")
            summary_end = text.find("建议1：")
            if summary_end == -1:
                summary_end = len(text)
            summary = text[summary_start:summary_end].strip()

        sug1 = TurnoverAnalysisService._extract_suggestion(text, "建议1：", "依据1：")
        if sug1:
            suggestions.append(sug1)

        if "建议2：" in text:
            sug2_start = text.find("建议2：")
            sug2_text = text[sug2_start:]
            sug2 = TurnoverAnalysisService._extract_suggestion(
                sug2_text, "建议2：", "依据2："
            )
            if sug2:
                suggestions.append(sug2)

        if not summary:
            summary = text

        return {
            "summary": summary,
            "suggestions": suggestions,
        }

    @staticmethod
    def _extract_suggestion(
        text: str, sug_label: str, evi_label: str
    ) -> AiSuggestion | None:
        """Extract a single suggestion and its evidence from text."""
        sug_start = text.find(sug_label)
        if sug_start == -1:
            return None

        sug_start += len(sug_label)
        evi_start = text.find(evi_label, sug_start)
        if evi_start == -1:
            return None

        suggestion = text[sug_start:evi_start].strip()
        evi_start += len(evi_label)

        next_sug = text.find("建议", evi_start)
        if next_sug == -1:
            evidence = text[evi_start:].strip()
        else:
            evidence = text[evi_start:next_sug].strip()

        if not suggestion:
            return None

        return AiSuggestion(suggestion=suggestion, evidence=evidence)
