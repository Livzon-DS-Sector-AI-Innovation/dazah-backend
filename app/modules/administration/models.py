"""Administration ORM models live here."""

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import BaseModel


class Vehicle(BaseModel):
    __tablename__ = "vehicles"
    __table_args__ = (
        Index("ix_vehicles_plate_number", "plate_number"),
        Index("ix_vehicles_status", "status"),
        {"schema": "administration"},
    )

    plate_number: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=False, comment="车牌号"
    )
    brand: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="品牌")
    model: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="型号")
    color: Mapped[str | None] = mapped_column(String(32), nullable=True, comment="颜色")
    purchase_date: Mapped[date | None] = mapped_column(Date, nullable=True, comment="购买日期")
    mileage: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="行驶里程")
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="可用", server_default="可用", comment="状态: 可用, 维修中, 已报废"
    )
    owner_department: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="所属部门")
    feishu_record_id: Mapped[str | None] = mapped_column(
        String(32), nullable=True, comment="飞书多维表格 record_id"
    )
    feishu_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="上次飞书同步时间"
    )
    photo_data: Mapped[str | None] = mapped_column(Text, nullable=True, comment="车辆照片base64数据")
    photo_type: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="照片MIME类型")
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")


class VehicleRequest(BaseModel):
    __tablename__ = "vehicle_requests"
    __table_args__ = (
        Index("ix_vehicle_requests_applicant", "applicant_name"),
        Index("ix_vehicle_requests_status", "status"),
        {"schema": "administration"},
    )

    applicant_name: Mapped[str] = mapped_column(String(64), nullable=False, comment="申请人姓名")
    applicant_department: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="申请人部门")
    applicant_phone: Mapped[str | None] = mapped_column(String(32), nullable=True, comment="联系电话")
    vehicle_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("administration.vehicles.id"), nullable=True, comment="分配车辆ID"
    )
    purpose: Mapped[str] = mapped_column(Text, nullable=False, comment="用车事由")
    destination: Mapped[str | None] = mapped_column(String(256), nullable=True, comment="目的地")
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="开始时间")
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="结束时间")
    passengers: Mapped[int | None] = mapped_column(Integer, nullable=True, default=1, comment="乘车人数")
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="待审批", server_default="待审批", comment="状态: 待审批, 已通过, 已拒绝, 已完成"
    )
    approver: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="审批人")
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="审批时间")
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")


class Regulation(BaseModel):
    __tablename__ = "regulations"
    __table_args__ = (
        Index("ix_regulations_title", "title"),
        {"schema": "administration"},
    )

    title: Mapped[str] = mapped_column(String(256), nullable=False, comment="制度名称")
    category: Mapped[str] = mapped_column(String(32), nullable=False, default="其它", server_default="其它", comment="类别: 人事, 行政, 其它")
    version: Mapped[str | None] = mapped_column(String(32), nullable=True, comment="版本号")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="制度内容")
    file_name: Mapped[str | None] = mapped_column(String(256), nullable=True, comment="原始文件名")
    file_type: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="文件类型")
    file_data: Mapped[str | None] = mapped_column(Text, nullable=True, comment="原始文件base64数据")
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")


class ITServiceTicket(BaseModel):
    __tablename__ = "it_service_tickets"
    __table_args__ = (
        Index("ix_it_tickets_requester", "requester_name"),
        Index("ix_it_tickets_status", "status"),
        Index("ix_it_tickets_type", "ticket_type"),
        {"schema": "administration"},
    )

    ticket_no: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=False, comment="工单编号"
    )
    requester_name: Mapped[str] = mapped_column(String(64), nullable=False, comment="报障人姓名")
    requester_department: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="报障人部门")
    requester_phone: Mapped[str | None] = mapped_column(String(32), nullable=True, comment="联系电话")
    ticket_type: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="工单类型: 硬件故障, 软件问题, 网络问题, 账号权限, 其他"
    )
    priority: Mapped[str] = mapped_column(
        String(16), nullable=False, default="中", server_default="中", comment="优先级: 低, 中, 高, 紧急"
    )
    title: Mapped[str] = mapped_column(String(128), nullable=False, comment="问题标题")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="问题描述")
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="待处理", server_default="待处理", comment="状态: 待处理, 处理中, 已解决, 已关闭"
    )
    assigned_to: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="指派给")
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="解决时间")
    solution: Mapped[str | None] = mapped_column(Text, nullable=True, comment="解决方案")
    feishu_record_id: Mapped[str | None] = mapped_column(
        String(32), nullable=True, comment="飞书多维表格 record_id"
    )
    feishu_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="上次飞书同步时间"
    )
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")


class GiftInventory(BaseModel):
    __tablename__ = "gift_inventories"
    __table_args__ = (
        Index("ix_gift_inventories_name", "name"),
        Index("ix_gift_inventories_status", "status"),
        {"schema": "administration"},
    )

    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="物品名称")
    specification: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="规格")
    unit: Mapped[str | None] = mapped_column(String(16), nullable=True, comment="计量单位")
    opening_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0", comment="月初库存")
    incoming_qty: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="本期入库/领用数量")
    closing_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0", comment="月底库存")
    unit_price: Mapped[float | None] = mapped_column(Numeric(14, 4), nullable=True, comment="单价")
    total_amount: Mapped[float | None] = mapped_column(Numeric(14, 4), nullable=True, comment="金额")
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="可用", server_default="可用", comment="状态: 可用, 库存不足, 停用"
    )
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")
