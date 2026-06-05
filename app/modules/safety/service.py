"""Safety business workflows."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.safety.models import (
    Accident,
    HazardReport,
    SafetyCheck,
    SafetyTraining,
    TrainingRecord,
)
from app.modules.safety.repository import SafetyRepository
from app.modules.safety.schemas import (
    AccidentCreate,
    AccidentUpdate,
    HazardReportCreate,
    HazardReportUpdate,
    SafetyCheckCreate,
    SafetyCheckUpdate,
    SafetyTrainingCreate,
    SafetyTrainingUpdate,
    TrainingRecordCreate,
    TrainingRecordUpdate,
)


class SafetyService:
    """Safety module service"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = SafetyRepository(session)

    # ==================== SafetyCheck Operations ====================

    async def get_checks(
        self,
        skip: int = 0,
        limit: int = 20,
        status: str | None = None,
        check_type: str | None = None,
        department: str | None = None,
    ) -> tuple[list[SafetyCheck], int]:
        """获取安全检查列表"""
        return await self.repo.get_checks(skip, limit, status, check_type, department)

    async def get_check(self, check_id: uuid.UUID) -> SafetyCheck | None:
        """获取安全检查详情"""
        return await self.repo.get_check_by_id(check_id)

    async def create_check(self, data: SafetyCheckCreate) -> SafetyCheck:
        """创建安全检查"""
        check_data = data.model_dump()
        return await self.repo.create_check(check_data)

    async def update_check(
        self, check_id: uuid.UUID, data: SafetyCheckUpdate
    ) -> SafetyCheck | None:
        """更新安全检查"""
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        return await self.repo.update_check(check_id, update_data)

    async def submit_check(self, check_id: uuid.UUID) -> SafetyCheck | None:
        """提交安全检查（草稿→已提交）"""
        check = await self.repo.get_check_by_id(check_id)
        if not check or check.status != "draft":
            return None
        return await self.repo.update_check(check_id, {"status": "submitted"})

    async def review_check(
        self, check_id: uuid.UUID, result: str
    ) -> SafetyCheck | None:
        """审核安全检查"""
        check = await self.repo.get_check_by_id(check_id)
        if not check or check.status not in ("submitted",):
            return None
        return await self.repo.update_check(
            check_id, {"status": "reviewed", "result": result}
        )

    async def close_check(self, check_id: uuid.UUID) -> SafetyCheck | None:
        """关闭安全检查"""
        check = await self.repo.get_check_by_id(check_id)
        if not check or check.status not in ("reviewed",):
            return None
        return await self.repo.update_check(check_id, {"status": "closed"})

    async def delete_check(self, check_id: uuid.UUID) -> bool:
        """删除安全检查"""
        return await self.repo.delete_check(check_id)

    # ==================== HazardReport Operations ====================

    async def get_hazards(
        self,
        skip: int = 0,
        limit: int = 20,
        status: str | None = None,
        hazard_type: str | None = None,
        hazard_level: str | None = None,
        department: str | None = None,
    ) -> tuple[list[HazardReport], int]:
        """获取隐患列表"""
        return await self.repo.get_hazards(
            skip, limit, status, hazard_type, hazard_level, department
        )

    async def get_hazard(self, hazard_id: uuid.UUID) -> HazardReport | None:
        """获取隐患详情"""
        return await self.repo.get_hazard_by_id(hazard_id)

    async def create_hazard(self, data: HazardReportCreate) -> HazardReport:
        """创建隐患"""
        hazard_data = data.model_dump()
        return await self.repo.create_hazard(hazard_data)

    async def update_hazard(
        self, hazard_id: uuid.UUID, data: HazardReportUpdate
    ) -> HazardReport | None:
        """更新隐患"""
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        return await self.repo.update_hazard(hazard_id, update_data)

    async def start_rectification(self, hazard_id: uuid.UUID) -> HazardReport | None:
        """开始整改"""
        hazard = await self.repo.get_hazard_by_id(hazard_id)
        if not hazard or hazard.rectification_status != "pending":
            return None
        return await self.repo.update_hazard(
            hazard_id, {"rectification_status": "in_progress"}
        )

    async def complete_rectification(self, hazard_id: uuid.UUID) -> HazardReport | None:
        """完成整改"""
        hazard = await self.repo.get_hazard_by_id(hazard_id)
        if not hazard or hazard.rectification_status != "in_progress":
            return None
        return await self.repo.update_hazard(
            hazard_id, {"rectification_status": "completed"}
        )

    async def verify_rectification(
        self,
        hazard_id: uuid.UUID,
        verified_by: uuid.UUID,
        verified_by_name: str,
        passed: bool,
    ) -> HazardReport | None:
        """验证整改"""
        hazard = await self.repo.get_hazard_by_id(hazard_id)
        if not hazard or hazard.rectification_status != "completed":
            return None
        update_data: dict[str, Any] = {
            "rectification_status": "verified",
            "verified_by": verified_by,
            "verified_by_name": verified_by_name,
            "verified_at": datetime.now(),
            "status": "closed" if passed else "open",
        }
        return await self.repo.update_hazard(hazard_id, update_data)

    async def delete_hazard(self, hazard_id: uuid.UUID) -> bool:
        """删除隐患"""
        return await self.repo.delete_hazard(hazard_id)

    # ==================== Accident Operations ====================

    async def get_accidents(
        self,
        skip: int = 0,
        limit: int = 20,
        status: str | None = None,
        accident_type: str | None = None,
        accident_level: str | None = None,
    ) -> tuple[list[Accident], int]:
        """获取事故列表"""
        return await self.repo.get_accidents(
            skip, limit, status, accident_type, accident_level
        )

    async def get_accident(self, accident_id: uuid.UUID) -> Accident | None:
        """获取事故详情"""
        return await self.repo.get_accident_by_id(accident_id)

    async def create_accident(self, data: AccidentCreate) -> Accident:
        """创建事故"""
        accident_data = data.model_dump()
        return await self.repo.create_accident(accident_data)

    async def update_accident(
        self, accident_id: uuid.UUID, data: AccidentUpdate
    ) -> Accident | None:
        """更新事故"""
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        return await self.repo.update_accident(accident_id, update_data)

    async def investigate_accident(
        self,
        accident_id: uuid.UUID,
        investigator: uuid.UUID,
        investigator_name: str,
    ) -> Accident | None:
        """开始调查事故"""
        accident = await self.repo.get_accident_by_id(accident_id)
        if not accident or accident.status != "reported":
            return None
        return await self.repo.update_accident(
            accident_id,
            {
                "status": "investigating",
                "investigator": investigator,
                "investigator_name": investigator_name,
            },
        )

    async def resolve_accident(
        self,
        accident_id: uuid.UUID,
        direct_cause: str,
        root_cause: str,
        handling_measures: str,
        corrective_actions: str | None = None,
    ) -> Accident | None:
        """处理并解决事故"""
        accident = await self.repo.get_accident_by_id(accident_id)
        if not accident or accident.status != "investigating":
            return None
        return await self.repo.update_accident(
            accident_id,
            {
                "status": "resolved",
                "direct_cause": direct_cause,
                "root_cause": root_cause,
                "handling_measures": handling_measures,
                "corrective_actions": corrective_actions,
            },
        )

    async def close_accident(self, accident_id: uuid.UUID) -> Accident | None:
        """关闭事故"""
        accident = await self.repo.get_accident_by_id(accident_id)
        if not accident or accident.status != "resolved":
            return None
        return await self.repo.update_accident(accident_id, {"status": "closed"})

    async def delete_accident(self, accident_id: uuid.UUID) -> bool:
        """删除事故"""
        return await self.repo.delete_accident(accident_id)

    # ==================== SafetyTraining Operations ====================

    async def get_trainings(
        self,
        skip: int = 0,
        limit: int = 20,
        status: str | None = None,
        training_type: str | None = None,
        department: str | None = None,
    ) -> tuple[list[SafetyTraining], int]:
        """获取安全培训列表"""
        return await self.repo.get_trainings(skip, limit, status, training_type, department)

    async def get_training(self, training_id: uuid.UUID) -> SafetyTraining | None:
        """获取安全培训详情"""
        return await self.repo.get_training_by_id(training_id)

    async def create_training(self, data: SafetyTrainingCreate) -> SafetyTraining:
        """创建安全培训"""
        training_data = data.model_dump()
        return await self.repo.create_training(training_data)

    async def update_training(
        self, training_id: uuid.UUID, data: SafetyTrainingUpdate
    ) -> SafetyTraining | None:
        """更新安全培训"""
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        return await self.repo.update_training(training_id, update_data)

    async def start_training(self, training_id: uuid.UUID) -> SafetyTraining | None:
        """开始培训（草稿→进行中）"""
        training = await self.repo.get_training_by_id(training_id)
        if not training or training.status != "draft":
            return None
        return await self.repo.update_training(training_id, {"status": "in_progress"})

    async def complete_training(self, training_id: uuid.UUID) -> SafetyTraining | None:
        """完成培训"""
        training = await self.repo.get_training_by_id(training_id)
        if not training or training.status != "in_progress":
            return None
        return await self.repo.update_training(training_id, {"status": "completed"})

    async def archive_training(self, training_id: uuid.UUID) -> SafetyTraining | None:
        """归档培训"""
        training = await self.repo.get_training_by_id(training_id)
        if not training or training.status != "completed":
            return None
        return await self.repo.update_training(training_id, {"status": "archived"})

    async def delete_training(self, training_id: uuid.UUID) -> bool:
        """删除安全培训"""
        return await self.repo.delete_training(training_id)

    # ==================== TrainingRecord Operations ====================

    async def get_training_records(self, training_id: uuid.UUID) -> list[TrainingRecord]:
        """获取培训记录列表"""
        return await self.repo.get_records_by_training(training_id)

    async def create_training_record(self, data: TrainingRecordCreate) -> TrainingRecord:
        """创建培训记录"""
        record_data = data.model_dump()
        return await self.repo.create_training_record(record_data)

    async def update_training_record(
        self, record_id: uuid.UUID, data: TrainingRecordUpdate
    ) -> TrainingRecord | None:
        """更新培训记录"""
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        return await self.repo.update_training_record(record_id, update_data)

    async def batch_create_records(
        self, training_id: uuid.UUID, records: list[TrainingRecordCreate]
    ) -> list[TrainingRecord]:
        """批量创建培训签到记录"""
        result = []
        for record in records:
            record_data = record.model_dump()
            record_data["training_id"] = training_id
            item = await self.repo.create_training_record(record_data)
            result.append(item)
        return result

    async def delete_training_record(self, record_id: uuid.UUID) -> bool:
        """删除培训记录"""
        return await self.repo.delete_training_record(record_id)
