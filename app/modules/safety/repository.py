"""Safety database queries."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.safety.models import (
    Accident,
    HazardReport,
    SafetyCheck,
    SafetyTraining,
    TrainingRecord,
)


class SafetyRepository:
    """Safety module repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

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
        query = select(SafetyCheck).where(SafetyCheck.is_deleted == False)

        if status:
            query = query.where(SafetyCheck.status == status)
        if check_type:
            query = query.where(SafetyCheck.check_type == check_type)
        if department:
            query = query.where(SafetyCheck.department == department)

        count_query = select(func.count(SafetyCheck.id)).where(SafetyCheck.is_deleted == False)
        if status:
            count_query = count_query.where(SafetyCheck.status == status)
        if check_type:
            count_query = count_query.where(SafetyCheck.check_type == check_type)
        if department:
            count_query = count_query.where(SafetyCheck.department == department)

        total = await self.session.scalar(count_query)
        query = query.offset(skip).limit(limit).order_by(SafetyCheck.created_at.desc())
        result = await self.session.execute(query)
        items = list(result.scalars().all())
        return items, total or 0

    async def get_check_by_id(self, check_id: uuid.UUID) -> SafetyCheck | None:
        """获取安全检查详情"""
        query = (
            select(SafetyCheck)
            .options(selectinload(SafetyCheck.hazards))
            .where(SafetyCheck.id == check_id, SafetyCheck.is_deleted == False)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_check(self, data: dict[str, Any]) -> SafetyCheck:
        """创建安全检查"""
        item = SafetyCheck(**data)
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def update_check(self, check_id: uuid.UUID, data: dict[str, Any]) -> SafetyCheck | None:
        """更新安全检查"""
        query = (
            update(SafetyCheck)
            .where(SafetyCheck.id == check_id, SafetyCheck.is_deleted == False)
            .values(**data)
            .returning(SafetyCheck)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def delete_check(self, check_id: uuid.UUID) -> bool:
        """删除安全检查（软删除）"""
        query = (
            update(SafetyCheck)
            .where(SafetyCheck.id == check_id, SafetyCheck.is_deleted == False)
            .values(is_deleted=True)
        )
        result = await self.session.execute(query)
        return result.rowcount > 0

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
        query = select(HazardReport).where(HazardReport.is_deleted == False)

        if status:
            query = query.where(HazardReport.status == status)
        if hazard_type:
            query = query.where(HazardReport.hazard_type == hazard_type)
        if hazard_level:
            query = query.where(HazardReport.hazard_level == hazard_level)
        if department:
            query = query.where(HazardReport.department == department)

        count_query = select(func.count(HazardReport.id)).where(HazardReport.is_deleted == False)
        if status:
            count_query = count_query.where(HazardReport.status == status)
        if hazard_type:
            count_query = count_query.where(HazardReport.hazard_type == hazard_type)
        if hazard_level:
            count_query = count_query.where(HazardReport.hazard_level == hazard_level)
        if department:
            count_query = count_query.where(HazardReport.department == department)

        total = await self.session.scalar(count_query)
        query = query.offset(skip).limit(limit).order_by(HazardReport.created_at.desc())
        result = await self.session.execute(query)
        items = list(result.scalars().all())
        return items, total or 0

    async def get_hazard_by_id(self, hazard_id: uuid.UUID) -> HazardReport | None:
        """获取隐患详情"""
        query = select(HazardReport).where(
            HazardReport.id == hazard_id, HazardReport.is_deleted == False
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_hazard(self, data: dict[str, Any]) -> HazardReport:
        """创建隐患"""
        item = HazardReport(**data)
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def update_hazard(self, hazard_id: uuid.UUID, data: dict[str, Any]) -> HazardReport | None:
        """更新隐患"""
        query = (
            update(HazardReport)
            .where(HazardReport.id == hazard_id, HazardReport.is_deleted == False)
            .values(**data)
            .returning(HazardReport)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def delete_hazard(self, hazard_id: uuid.UUID) -> bool:
        """删除隐患（软删除）"""
        query = (
            update(HazardReport)
            .where(HazardReport.id == hazard_id, HazardReport.is_deleted == False)
            .values(is_deleted=True)
        )
        result = await self.session.execute(query)
        return result.rowcount > 0

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
        query = select(Accident).where(Accident.is_deleted == False)

        if status:
            query = query.where(Accident.status == status)
        if accident_type:
            query = query.where(Accident.accident_type == accident_type)
        if accident_level:
            query = query.where(Accident.accident_level == accident_level)

        count_query = select(func.count(Accident.id)).where(Accident.is_deleted == False)
        if status:
            count_query = count_query.where(Accident.status == status)
        if accident_type:
            count_query = count_query.where(Accident.accident_type == accident_type)
        if accident_level:
            count_query = count_query.where(Accident.accident_level == accident_level)

        total = await self.session.scalar(count_query)
        query = query.offset(skip).limit(limit).order_by(Accident.created_at.desc())
        result = await self.session.execute(query)
        items = list(result.scalars().all())
        return items, total or 0

    async def get_accident_by_id(self, accident_id: uuid.UUID) -> Accident | None:
        """获取事故详情"""
        query = select(Accident).where(
            Accident.id == accident_id, Accident.is_deleted == False
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_accident(self, data: dict[str, Any]) -> Accident:
        """创建事故"""
        item = Accident(**data)
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def update_accident(
        self, accident_id: uuid.UUID, data: dict[str, Any]
    ) -> Accident | None:
        """更新事故"""
        query = (
            update(Accident)
            .where(Accident.id == accident_id, Accident.is_deleted == False)
            .values(**data)
            .returning(Accident)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def delete_accident(self, accident_id: uuid.UUID) -> bool:
        """删除事故（软删除）"""
        query = (
            update(Accident)
            .where(Accident.id == accident_id, Accident.is_deleted == False)
            .values(is_deleted=True)
        )
        result = await self.session.execute(query)
        return result.rowcount > 0

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
        query = select(SafetyTraining).where(SafetyTraining.is_deleted == False)

        if status:
            query = query.where(SafetyTraining.status == status)
        if training_type:
            query = query.where(SafetyTraining.training_type == training_type)
        if department:
            query = query.where(SafetyTraining.department == department)

        count_query = select(func.count(SafetyTraining.id)).where(
            SafetyTraining.is_deleted == False
        )
        if status:
            count_query = count_query.where(SafetyTraining.status == status)
        if training_type:
            count_query = count_query.where(SafetyTraining.training_type == training_type)
        if department:
            count_query = count_query.where(SafetyTraining.department == department)

        total = await self.session.scalar(count_query)
        query = query.offset(skip).limit(limit).order_by(SafetyTraining.created_at.desc())
        result = await self.session.execute(query)
        items = list(result.scalars().all())
        return items, total or 0

    async def get_training_by_id(self, training_id: uuid.UUID) -> SafetyTraining | None:
        """获取安全培训详情"""
        query = (
            select(SafetyTraining)
            .options(selectinload(SafetyTraining.records))
            .where(SafetyTraining.id == training_id, SafetyTraining.is_deleted == False)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_training(self, data: dict[str, Any]) -> SafetyTraining:
        """创建安全培训"""
        item = SafetyTraining(**data)
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def update_training(
        self, training_id: uuid.UUID, data: dict[str, Any]
    ) -> SafetyTraining | None:
        """更新安全培训"""
        query = (
            update(SafetyTraining)
            .where(SafetyTraining.id == training_id, SafetyTraining.is_deleted == False)
            .values(**data)
            .returning(SafetyTraining)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def delete_training(self, training_id: uuid.UUID) -> bool:
        """删除安全培训（软删除）"""
        query = (
            update(SafetyTraining)
            .where(SafetyTraining.id == training_id, SafetyTraining.is_deleted == False)
            .values(is_deleted=True)
        )
        result = await self.session.execute(query)
        return result.rowcount > 0

    # ==================== TrainingRecord Operations ====================

    async def get_records_by_training(self, training_id: uuid.UUID) -> list[TrainingRecord]:
        """获取培训记录列表"""
        query = select(TrainingRecord).where(
            TrainingRecord.training_id == training_id, TrainingRecord.is_deleted == False
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create_training_record(self, data: dict[str, Any]) -> TrainingRecord:
        """创建培训记录"""
        item = TrainingRecord(**data)
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def update_training_record(
        self, record_id: uuid.UUID, data: dict[str, Any]
    ) -> TrainingRecord | None:
        """更新培训记录"""
        query = (
            update(TrainingRecord)
            .where(TrainingRecord.id == record_id, TrainingRecord.is_deleted == False)
            .values(**data)
            .returning(TrainingRecord)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def delete_training_record(self, record_id: uuid.UUID) -> bool:
        """删除培训记录（软删除）"""
        query = (
            update(TrainingRecord)
            .where(TrainingRecord.id == record_id, TrainingRecord.is_deleted == False)
            .values(is_deleted=True)
        )
        result = await self.session.execute(query)
        return result.rowcount > 0
