"""Regulatory Tracker repository layer."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.regulatory_tracker.models import (
    DataSource,
    DataChannel,
    RegulatoryDocument,
    SyncJob,
    SyncJobPage,
)


# ============ DataSource ============

async def get_data_source_by_code(db: AsyncSession, code: str) -> DataSource | None:
    """根据编码获取数据源"""
    result = await db.execute(
        select(DataSource).where(
            DataSource.code == code,
            DataSource.is_deleted == False,  # noqa: E712
        )
    )
    return result.scalar_one_or_none()


async def get_data_source_by_id(db: AsyncSession, source_id: uuid.UUID) -> DataSource | None:
    """根据ID获取数据源"""
    result = await db.execute(
        select(DataSource).where(
            DataSource.id == source_id,
            DataSource.is_deleted == False,  # noqa: E712
        )
    )
    return result.scalar_one_or_none()


# ============ DataChannel ============

async def get_channel_by_code(
    db: AsyncSession, source_id: uuid.UUID, code: str
) -> DataChannel | None:
    """根据编码获取栏目"""
    result = await db.execute(
        select(DataChannel).where(
            DataChannel.source_id == source_id,
            DataChannel.code == code,
            DataChannel.is_deleted == False,  # noqa: E712
        )
    )
    return result.scalar_one_or_none()


async def get_channel_by_id(db: AsyncSession, channel_id: uuid.UUID) -> DataChannel | None:
    """根据ID获取栏目"""
    result = await db.execute(
        select(DataChannel).where(
            DataChannel.id == channel_id,
            DataChannel.is_deleted == False,  # noqa: E712
        )
    )
    return result.scalar_one_or_none()


# ============ RegulatoryDocument ============

async def get_document_by_document_id(
    db: AsyncSession,
    source_id: uuid.UUID,
    channel_id: uuid.UUID,
    document_id: str,
) -> RegulatoryDocument | None:
    """根据 document_id 查询文档（去重键）"""
    result = await db.execute(
        select(RegulatoryDocument).where(
            RegulatoryDocument.source_id == source_id,
            RegulatoryDocument.channel_id == channel_id,
            RegulatoryDocument.document_id == document_id,
            RegulatoryDocument.is_deleted == False,  # noqa: E712
        )
    )
    return result.scalar_one_or_none()


async def create_document(db: AsyncSession, data: dict[str, Any]) -> RegulatoryDocument:
    """创建新文档"""
    doc = RegulatoryDocument(**data)
    db.add(doc)
    await db.flush()
    return doc


async def update_document(
    db: AsyncSession, doc_id: uuid.UUID, data: dict[str, Any]
) -> RegulatoryDocument | None:
    """更新文档"""
    result = await db.execute(
        select(RegulatoryDocument).where(RegulatoryDocument.id == doc_id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        return None
    for key, value in data.items():
        if hasattr(doc, key):
            setattr(doc, key, value)
    await db.flush()
    return doc


async def count_documents(
    db: AsyncSession, source_id: uuid.UUID, channel_id: uuid.UUID
) -> int:
    """统计文档数量"""
    result = await db.execute(
        select(func.count(RegulatoryDocument.id)).where(
            RegulatoryDocument.source_id == source_id,
            RegulatoryDocument.channel_id == channel_id,
            RegulatoryDocument.is_deleted == False,  # noqa: E712
        )
    )
    return result.scalar() or 0


# ============ SyncJob ============

async def create_sync_job(db: AsyncSession, data: dict[str, Any]) -> SyncJob:
    """创建同步任务"""
    job = SyncJob(**data)
    db.add(job)
    await db.flush()
    return job


async def get_sync_job_by_id(db: AsyncSession, job_id: uuid.UUID) -> SyncJob | None:
    """根据ID获取同步任务"""
    result = await db.execute(
        select(SyncJob).where(SyncJob.id == job_id)
    )
    return result.scalar_one_or_none()


async def update_sync_job(
    db: AsyncSession, job_id: uuid.UUID, data: dict[str, Any]
) -> SyncJob | None:
    """更新同步任务"""
    job = await get_sync_job_by_id(db, job_id)
    if not job:
        return None
    for key, value in data.items():
        if hasattr(job, key):
            setattr(job, key, value)
    await db.flush()
    return job


# ============ SyncJobPage ============

async def create_sync_job_page(db: AsyncSession, data: dict[str, Any]) -> SyncJobPage:
    """创建同步任务分页记录"""
    page = SyncJobPage(**data)
    db.add(page)
    await db.flush()
    return page


async def update_sync_job_page(
    db: AsyncSession, page_id: uuid.UUID, data: dict[str, Any]
) -> SyncJobPage | None:
    """更新同步任务分页记录"""
    result = await db.execute(
        select(SyncJobPage).where(SyncJobPage.id == page_id)
    )
    page = result.scalar_one_or_none()
    if not page:
        return None
    for key, value in data.items():
        if hasattr(page, key):
            setattr(page, key, value)
    await db.flush()
    return page
