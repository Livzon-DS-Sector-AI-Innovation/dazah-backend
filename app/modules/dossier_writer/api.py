"""Dossier Writer API endpoints."""
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import success_response, error_response
from .schemas import (
    ProductDossierCreate, ProductDossierUpdate,
    ProductDossierResponse, ProductDossierListResponse,
    ChapterResponse, ChapterDetailResponse,
    AssetResponse, AssetUploadResponse,
    ParseResultResponse, ExportRequest, ExportResponse,
)
from .service import DossierService

router = APIRouter()


# ====== Product Dossier ======

@router.post("/products", response_model=dict)
async def create_product_dossier(
    data: ProductDossierCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建品种资料"""
    service = DossierService(db)
    try:
        dossier = await service.create_product_dossier(data)
        return success_response(
            data=ProductDossierResponse.model_validate(dossier),
            message="创建成功"
        )
    except ValueError as e:
        return error_response(message=str(e), status_code=400)


@router.get("/products", response_model=dict)
async def list_product_dossiers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """获取品种资料列表"""
    service = DossierService(db)
    items, total = await service.list_product_dossiers(skip, limit)
    return success_response(
        data={
            "items": [ProductDossierListResponse.model_validate(i) for i in items],
            "total": total,
            "skip": skip,
            "limit": limit,
        },
        message="获取成功"
    )


@router.get("/products/{dossier_id}", response_model=dict)
async def get_product_dossier(
    dossier_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """获取品种资料详情"""
    service = DossierService(db)
    dossier = await service.get_product_dossier(dossier_id)
    if not dossier:
        raise HTTPException(status_code=404, detail="品种资料不存在")
    return success_response(
        data=ProductDossierResponse.model_validate(dossier),
        message="获取成功"
    )


@router.put("/products/{dossier_id}", response_model=dict)
async def update_product_dossier(
    dossier_id: UUID,
    data: ProductDossierUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新品种资料"""
    service = DossierService(db)
    dossier = await service.update_product_dossier(dossier_id, data)
    if not dossier:
        raise HTTPException(status_code=404, detail="品种资料不存在")
    return success_response(
        data=ProductDossierResponse.model_validate(dossier),
        message="更新成功"
    )


@router.delete("/products/{dossier_id}", response_model=dict)
async def delete_product_dossier(
    dossier_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """删除品种资料"""
    service = DossierService(db)
    success = await service.delete_product_dossier(dossier_id)
    if not success:
        raise HTTPException(status_code=404, detail="品种资料不存在")
    return success_response(message="删除成功")


# ====== Template Upload ======

@router.post("/products/{dossier_id}/templates", response_model=dict)
async def upload_templates(
    dossier_id: UUID,
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
):
    """批量上传模板文件"""
    service = DossierService(db)
    
    results = []
    for file in files:
        # 验证文件类型
        if not file.filename or not file.filename.lower().endswith('.docx'):
            results.append({
                "filename": file.filename,
                "status": "failed",
                "error": "仅支持 .docx 格式文件"
            })
            continue
        
        try:
            # 读取文件内容
            content = await file.read()
            
            # 保存模板
            template = await service.save_template_file(dossier_id, file.filename, content)
            
            results.append({
                "file_id": str(template.id),
                "filename": template.original_filename,
                "file_path": template.file_path,
                "file_size": template.file_size,
                "status": "success"
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "failed",
                "error": str(e)
            })
    
    # 更新品种状态为 template_uploaded
    await service.repo.update_product_dossier(dossier_id, parse_status="template_uploaded")
    await service.db.commit()
    
    success_count = sum(1 for r in results if r["status"] == "success")
    failed_count = len(results) - success_count
    
    # 自动触发匹配
    match_result = await service.match_assets_to_chapters(dossier_id)
    
    return success_response(
        data={
            "results": results,
            "success_count": success_count,
            "failed_count": failed_count,
            "matched_count": match_result.get("matched_count", 0),
            "unmatched_files": match_result.get("unmatched_files", []),
        },
        message=f"上传完成：成功 {success_count} 个，匹配 {match_result.get('matched_count', 0)} 个"
    )


# ====== Template Parsing ======

@router.post("/products/{dossier_id}/parse", response_model=dict)
async def parse_templates(
    dossier_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """解析模板生成章节树"""
    service = DossierService(db)
    result = await service.parse_templates(dossier_id)
    
    if result["success"]:
        return success_response(data=result, message=result["message"])
    else:
        return error_response(message=result["message"], detail=result.get("error"))


# ====== Chapter ======

@router.get("/products/{dossier_id}/chapters", response_model=dict)
async def get_chapter_tree(
    dossier_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """获取章节树"""
    service = DossierService(db)
    chapters = await service.get_chapter_tree(dossier_id)
    return success_response(data=chapters, message="获取成功")


@router.get("/chapters/{chapter_id}", response_model=dict)
async def get_chapter_detail(
    chapter_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """获取章节详情"""
    service = DossierService(db)
    chapter = await service.get_chapter_detail(chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")
    return success_response(data=chapter, message="获取成功")


# ====== Asset ======

@router.post("/chapters/{chapter_id}/assets", response_model=dict)
async def upload_asset(
    chapter_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """上传章节素材"""
    service = DossierService(db)
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")
    
    content = await file.read()
    asset = await service.upload_chapter_asset(chapter_id, file.filename, content)
    
    return success_response(
        data=AssetUploadResponse(
            id=asset.id,
            original_filename=asset.original_filename,
            file_path=asset.file_path,
            file_type=asset.file_type,
            file_size=asset.file_size,
            uploaded_at=asset.uploaded_at,
        ),
        message="素材上传成功"
    )


@router.get("/chapters/{chapter_id}/assets", response_model=dict)
async def list_assets(
    chapter_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """获取章节素材列表"""
    service = DossierService(db)
    assets = await service.list_chapter_assets(chapter_id)
    return success_response(
        data=[AssetResponse.model_validate(a) for a in assets],
        message="获取成功"
    )


@router.delete("/assets/{asset_id}", response_model=dict)
async def delete_asset(
    asset_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """删除素材"""
    service = DossierService(db)
    success = await service.delete_asset(asset_id)
    if not success:
        raise HTTPException(status_code=404, detail="素材不存在")
    return success_response(message="删除成功")


# ====== Export ======

@router.post("/products/{dossier_id}/export", response_model=dict)
async def export_dossier(
    dossier_id: UUID,
    data: ExportRequest,
    db: AsyncSession = Depends(get_db),
):
    """导出品种资料"""
    service = DossierService(db)
    result = await service.export_dossier(dossier_id, data.chapter_ids)
    
    if result["success"]:
        return success_response(data=result, message=result["message"])
    else:
        return error_response(message=result["message"])


@router.get("/products/{dossier_id}/download")
async def download_exported_file(
    dossier_id: UUID,
    filename: str = Query(..., description="文件名"),
    db: AsyncSession = Depends(get_db),
):
    """下载导出的文件"""
    service = DossierService(db)
    dossier = await service.repo.get_product_dossier(dossier_id)
    if not dossier:
        raise HTTPException(status_code=404, detail="品种资料不存在")
    
    from pathlib import Path
    file_path = Path(dossier.outputs_path) / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

@router.get("/chapters/{chapter_id}/preview", response_model=dict)
async def get_chapter_preview(
    chapter_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """获取章节预览内容"""
    service = DossierService(db)
    result = await service.get_chapter_preview(chapter_id)
    
    if result["success"]:
        return success_response(data=result, message="获取预览成功")
    else:
        return error_response(message=result["message"])


@router.post("/products/{dossier_id}/match-assets", response_model=dict)
async def match_assets_to_chapters(
    dossier_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """智能匹配素材到章节"""
    service = DossierService(db)
    result = await service.match_assets_to_chapters(dossier_id)
    
    if result["success"]:
        return success_response(data=result, message=result["message"])
    else:
        return error_response(message=result["message"])
