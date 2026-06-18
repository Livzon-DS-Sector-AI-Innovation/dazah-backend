"""Instrument Calibration Service (仪器校准管理业务逻辑层)

提供仪器设备台账、校准规则配置、校准记录、审批记录的业务逻辑处理
"""

from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from uuid import UUID
import re

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.quality.instrument_models import (
    InstrumentCalibration,
    InstrumentCalibrationRule,
    InstrumentCalibrationRecord,
    InstrumentCalibrationApproval,
)
from app.modules.quality.instrument_repository import (
    InstrumentRepository,
    CalibrationRuleRepository,
    CalibrationRecordRepository,
    CalibrationApprovalRepository,
)
from app.modules.quality.instrument_schemas import (
    InstrumentCreate,
    InstrumentUpdate,
    CalibrationRuleCreate,
    CalibrationRuleUpdate,
    CalibrationRecordCreate,
    CalibrationRecordUpdate,
    ApprovalCreate,
    InstrumentStatus,
    CalibrationResult,
    RecordStatus,
    ApprovalStatus,
    ApprovalType,
)


def generate_instrument_no() -> str:
    """生成仪器编号"""
    now = datetime.now()
    return f"INS{now.strftime('%Y%m%d%H%M')}"


def generate_calibration_no() -> str:
    """生成校准单据编号"""
    now = datetime.now()
    return f"CAL{now.strftime('%Y%m%d%H%M')}"


def calculate_next_calibration_date(
    calibration_date: datetime,
    cycle: int,
    unit: str
) -> datetime:
    """计算下次校准日期"""
    if unit == 'year':
        return calibration_date + timedelta(days=365 * cycle)
    else:  # month
        # 粗略计算每月30天
        return calibration_date + timedelta(days=30 * cycle)


class InstrumentService:
    """仪器设备Service"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = InstrumentRepository(session)
        self.rule_repository = CalibrationRuleRepository(session)

    async def create_instrument(
        self,
        data: InstrumentCreate,
        user_id: Optional[UUID] = None
    ) -> InstrumentCalibration:
        """创建仪器"""
        # 检查编号是否已存在
        existing = await self.repository.get_by_no(data.instrument_no)
        if existing:
            raise ValueError(f"仪器编号 {data.instrument_no} 已存在")

        # 构建创建数据
        instrument_data = data.model_dump()
        instrument_data['status'] = InstrumentStatus.DRAFT.value
        instrument_data['created_by'] = user_id
        instrument_data['updated_by'] = user_id

        return await self.repository.create(instrument_data)

    async def get_instrument(self, instrument_id: UUID) -> InstrumentCalibration:
        """获取仪器详情"""
        instrument = await self.repository.get_by_id(instrument_id)
        if not instrument:
            raise ValueError("仪器不存在")
        return instrument

    async def update_instrument(
        self,
        instrument_id: UUID,
        data: InstrumentUpdate,
        user_id: Optional[UUID] = None
    ) -> InstrumentCalibration:
        """更新仪器"""
        existing = await self.repository.get_by_id(instrument_id)
        if not existing:
            raise ValueError("仪器不存在")

        # 草稿状态才能编辑基本信息
        if existing.status not in [InstrumentStatus.DRAFT.value, InstrumentStatus.INACTIVE.value]:
            # 已提交的仪器只能更新特定字段
            pass

        update_data = data.model_dump(exclude_unset=True)
        update_data['updated_by'] = user_id

        return await self.repository.update(instrument_id, update_data)

    async def delete_instrument(self, instrument_id: UUID) -> bool:
        """删除仪器"""
        existing = await self.repository.get_by_id(instrument_id)
        if not existing:
            raise ValueError("仪器不存在")

        # 只能删除草稿状态的仪器
        if existing.status != InstrumentStatus.DRAFT.value:
            raise ValueError("只能删除草稿状态的仪器")

        return await self.repository.delete(instrument_id)

    async def list_instruments(
        self,
        instrument_no: Optional[str] = None,
        instrument_name: Optional[str] = None,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
        status: Optional[str] = None,
        is_overdue: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[InstrumentCalibration], int]:
        """获取仪器列表"""
        instruments, total = await self.repository.list_with_filter(
            instrument_no=instrument_no,
            instrument_name=instrument_name,
            category=category,
            is_active=is_active,
            status=status,
            is_overdue=is_overdue,
            page=page,
            page_size=page_size
        )

        # 如果需要过滤超期仪器
        if is_overdue:
            now = datetime.now()
            filtered = []
            for inst in instruments:
                rule = await self.rule_repository.get_by_instrument_id(inst.id)
                if rule and rule.next_calibration_date and rule.next_calibration_date < now:
                    filtered.append(inst)
            instruments = filtered
            total = len(filtered)

        return instruments, total

    async def submit_instrument(
        self,
        instrument_id: UUID,
        user_id: Optional[UUID] = None
    ) -> InstrumentCalibration:
        """提交仪器审核"""
        instrument = await self.repository.get_by_id(instrument_id)
        if not instrument:
            raise ValueError("仪器不存在")

        if instrument.status != InstrumentStatus.DRAFT.value:
            raise ValueError("只能提交草稿状态的仪器")

        # 检查是否已配置校准规则
        rule = await self.rule_repository.get_by_instrument_id(instrument_id)
        if not rule:
            raise ValueError("请先配置校准规则")

        # 更新状态
        return await self.repository.update(
            instrument_id,
            {'status': InstrumentStatus.SUBMITTED.value}
        )

    async def approve_instrument(
        self,
        instrument_id: UUID,
        approved: bool,
        comments: Optional[str] = None,
        approval_type: str = 'admin',
        user_id: Optional[UUID] = None,
        user_name: Optional[str] = None
    ) -> InstrumentCalibration:
        """审批仪器"""
        instrument = await self.repository.get_by_id(instrument_id)
        if not instrument:
            raise ValueError("仪器不存在")

        if approval_type == 'admin':
            if instrument.status != InstrumentStatus.SUBMITTED.value:
                raise ValueError("设备管理员只能审核已提交的仪器")
            new_status = (
                InstrumentStatus.QA_APPROVED.value if approved
                else InstrumentStatus.DRAFT.value
            )
        else:  # qa
            if instrument.status != InstrumentStatus.QA_APPROVED.value:
                raise ValueError("QA只能审核设备管理员已通过的仪器")
            new_status = (
                InstrumentStatus.ACTIVE.value if approved
                else InstrumentStatus.SUBMITTED.value
            )

        update_data = {'status': new_status, 'updated_by': user_id}

        # 如果是驳回
        if not approved:
            update_data['remark'] = (instrument.remark or '') + f"\n驳回原因：{comments}"

        return await self.repository.update(instrument_id, update_data)

    async def activate_instrument(
        self,
        instrument_id: UUID,
        user_id: Optional[UUID] = None
    ) -> InstrumentCalibration:
        """启用仪器"""
        instrument = await self.repository.get_by_id(instrument_id)
        if not instrument:
            raise ValueError("仪器不存在")

        return await self.repository.update(
            instrument_id,
            {
                'is_active': True,
                'status': InstrumentStatus.ACTIVE.value,
                'updated_by': user_id
            }
        )

    async def deactivate_instrument(
        self,
        instrument_id: UUID,
        reason: str,
        user_id: Optional[UUID] = None
    ) -> InstrumentCalibration:
        """停用仪器"""
        instrument = await self.repository.get_by_id(instrument_id)
        if not instrument:
            raise ValueError("仪器不存在")

        return await self.repository.update(
            instrument_id,
            {
                'is_active': False,
                'status': InstrumentStatus.INACTIVE.value,
                'deactivate_date': datetime.now(),
                'deactivate_reason': reason,
                'updated_by': user_id
            }
        )


class CalibrationRuleService:
    """校准规则Service"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = CalibrationRuleRepository(session)
        self.instrument_repository = InstrumentRepository(session)

    async def create_rule(
        self,
        data: CalibrationRuleCreate,
        user_id: Optional[UUID] = None
    ) -> InstrumentCalibrationRule:
        """创建校准规则"""
        # 检查仪器是否存在
        instrument = await self.instrument_repository.get_by_id(data.instrument_id)
        if not instrument:
            raise ValueError("仪器不存在")

        # 检查是否已存在规则
        existing = await self.repository.get_by_instrument_id(data.instrument_id)
        if existing:
            raise ValueError("该仪器已配置校准规则")

        # 构建创建数据
        rule_data = data.model_dump()
        rule_data['created_by'] = user_id
        rule_data['updated_by'] = user_id

        # 计算下次校准日期
        if rule_data.get('calibration_cycle') and rule_data.get('calibration_unit'):
            now = datetime.now()
            rule_data['next_calibration_date'] = calculate_next_calibration_date(
                now,
                rule_data['calibration_cycle'],
                rule_data['calibration_unit']
            )

        return await self.repository.create(rule_data)

    async def get_rule(self, rule_id: UUID) -> InstrumentCalibrationRule:
        """获取规则详情"""
        rule = await self.repository.get_by_id(rule_id)
        if not rule:
            raise ValueError("校准规则不存在")
        return rule

    async def update_rule(
        self,
        rule_id: UUID,
        data: CalibrationRuleUpdate,
        user_id: Optional[UUID] = None
    ) -> InstrumentCalibrationRule:
        """更新规则"""
        existing = await self.repository.get_by_id(rule_id)
        if not existing:
            raise ValueError("校准规则不存在")

        update_data = data.model_dump(exclude_unset=True)
        update_data['updated_by'] = user_id

        # 如果更新了周期，重新计算下次校准日期
        if update_data.get('calibration_cycle') or update_data.get('calibration_unit'):
            cycle = update_data.get('calibration_cycle', existing.calibration_cycle)
            unit = update_data.get('calibration_unit', existing.calibration_unit)
            if cycle and unit:
                base_date = existing.last_calibration_date or datetime.now()
                update_data['next_calibration_date'] = calculate_next_calibration_date(
                    base_date, cycle, unit
                )

        return await self.repository.update(rule_id, update_data)

    async def delete_rule(self, rule_id: UUID) -> bool:
        """删除规则"""
        existing = await self.repository.get_by_id(rule_id)
        if not existing:
            raise ValueError("校准规则不存在")

        return await self.repository.delete(rule_id)

    async def get_upcoming_calibrations(self, days: int = 30) -> List[InstrumentCalibrationRule]:
        """获取即将到期的校准计划"""
        return await self.repository.get_upcoming_calibrations(days)


class CalibrationRecordService:
    """校准记录Service"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = CalibrationRecordRepository(session)
        self.instrument_repository = InstrumentRepository(session)
        self.rule_repository = CalibrationRuleRepository(session)

    async def create_record(
        self,
        data: CalibrationRecordCreate,
        user_id: Optional[UUID] = None
    ) -> InstrumentCalibrationRecord:
        """创建校准记录"""
        # 检查仪器是否存在
        instrument = await self.instrument_repository.get_by_id(data.instrument_id)
        if not instrument:
            raise ValueError("仪器不存在")

        # 生成校准编号
        calibration_no = generate_calibration_no()

        # 构建创建数据
        record_data = data.model_dump()
        record_data['calibration_no'] = calibration_no
        record_data['status'] = RecordStatus.DRAFT.value
        record_data['created_by'] = user_id
        record_data['updated_by'] = user_id

        record = await self.repository.create(record_data)

        # 如果校准合格且有关联规则，更新规则的下次校准日期
        if record.calibration_result == CalibrationResult.QUALIFIED.value and record.rule_id:
            rule = await self.rule_repository.get_by_id(record.rule_id)
            if rule and rule.calibration_cycle and rule.calibration_unit:
                next_date = calculate_next_calibration_date(
                    record.calibration_date,
                    rule.calibration_cycle,
                    rule.calibration_unit
                )
                await self.rule_repository.update(
                    rule.id,
                    {
                        'last_calibration_date': record.calibration_date,
                        'next_calibration_date': next_date,
                        'updated_by': user_id
                    }
                )

        # 如果校准不合格，自动停用仪器
        if record.calibration_result == CalibrationResult.UNQUALIFIED.value:
            await self.instrument_repository.update(
                record.instrument_id,
                {
                    'is_active': False,
                    'status': InstrumentStatus.INACTIVE.value,
                    'deactivate_date': datetime.now(),
                    'deactivate_reason': f"校准不合格：{record.result_reason}",
                    'updated_by': user_id
                }
            )

        return record

    async def get_record(self, record_id: UUID) -> InstrumentCalibrationRecord:
        """获取记录详情"""
        record = await self.repository.get_by_id(record_id)
        if not record:
            raise ValueError("校准记录不存在")
        return record

    async def update_record(
        self,
        record_id: UUID,
        data: CalibrationRecordUpdate,
        user_id: Optional[UUID] = None
    ) -> InstrumentCalibrationRecord:
        """更新记录"""
        existing = await self.repository.get_by_id(record_id)
        if not existing:
            raise ValueError("校准记录不存在")

        # 草稿状态才能编辑
        if existing.status != RecordStatus.DRAFT.value:
            raise ValueError("只能编辑草稿状态的记录")

        update_data = data.model_dump(exclude_unset=True)
        update_data['updated_by'] = user_id

        return await self.repository.update(record_id, update_data)

    async def delete_record(self, record_id: UUID) -> bool:
        """删除记录"""
        existing = await self.repository.get_by_id(record_id)
        if not existing:
            raise ValueError("校准记录不存在")

        if existing.status != RecordStatus.DRAFT.value:
            raise ValueError("只能删除草稿状态的记录")

        return await self.repository.delete(record_id)

    async def list_records(
        self,
        instrument_id: Optional[str | UUID] = None,
        calibration_no: Optional[str] = None,
        calibration_result: Optional[str] = None,
        status: Optional[str] = None,
        calibration_method: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[InstrumentCalibrationRecord], int]:
        """获取校准记录列表"""
        return await self.repository.list_with_filter(
            instrument_id=instrument_id,
            calibration_no=calibration_no,
            calibration_result=calibration_result,
            status=status,
            calibration_method=calibration_method,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size
        )

    async def submit_record(
        self,
        record_id: UUID,
        user_id: Optional[UUID] = None
    ) -> InstrumentCalibrationRecord:
        """提交校准记录"""
        record = await self.repository.get_by_id(record_id)
        if not record:
            raise ValueError("校准记录不存在")

        if record.status != RecordStatus.DRAFT.value:
            raise ValueError("只能提交草稿状态的记录")

        return await self.repository.update(
            record_id,
            {'status': RecordStatus.SUBMITTED.value},
            user_id
        )

    async def approve_record(
        self,
        record_id: UUID,
        approved: bool,
        comments: Optional[str] = None,
        approval_type: str = 'admin',
        user_id: Optional[UUID] = None,
        user_name: Optional[str] = None
    ) -> InstrumentCalibrationRecord:
        """审批校准记录"""
        record = await self.repository.get_by_id(record_id)
        if not record:
            raise ValueError("校准记录不存在")

        if approval_type == 'admin':
            if record.status != RecordStatus.SUBMITTED.value:
                raise ValueError("设备管理员只能审核已提交的记录")
            new_status = (
                RecordStatus.QA_APPROVED.value if approved
                else RecordStatus.DRAFT.value
            )
        else:  # qa
            if record.status != RecordStatus.QA_APPROVED.value:
                raise ValueError("QA只能审核设备管理员已通过的记录")
            new_status = (
                RecordStatus.COMPLETED.value if approved
                else RecordStatus.SUBMITTED.value
            )

        return await self.repository.update(
            record_id,
            {'status': new_status, 'updated_by': user_id}
        )
