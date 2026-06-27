from urllib.parse import quote
from uuid import UUID

from fastapi import Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.response import paginated_response, success_response
from app.modules.procurement.contract_generator import (
    generate_contract,
    get_contract_template_metadata,
)
from app.modules.procurement.schemas import (
    ContractCategory,
    ContractGenerateRequest,
    ContractTemplateMetadata,
    InvoiceRecognitionRecordDeleteRequest,
    InvoiceRecognitionRecordDeleteResponse,
    InvoiceRecognitionRecordDeleteResult,
    InvoiceRecognitionRecordListResponse,
    InvoiceRecognitionRecordResponse,
    InvoiceRecognitionResponse,
)
from app.modules.procurement.service import (
    DuplicateInvoiceError,
    batch_delete_invoice_recognition_records,
    delete_invoice_recognition_record,
    list_invoice_recognition_records,
    recognize_and_store_invoice_pdf,
)
from app.shared.module_api import create_module_router
from app.shared.module_registry import MODULES_BY_CODE

router = create_module_router(MODULES_BY_CODE["procurement"])

settings = get_settings()
MAX_INVOICE_PDF_UPLOAD_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
INVOICE_UPLOAD_CHUNK_SIZE = 1024 * 1024


@router.post(
    "/invoices/recognize",
    summary="识别采购发票 PDF",
    description=(
        "从电子发票 PDF 中识别发票号码、开票日期、销售方名称、"
        "税额合计和价税合计（小写）。开启明细识别时额外识别项目名称、单位和数量。"
    ),
    response_model=InvoiceRecognitionResponse,
)
async def recognize_invoice(
    include_details: bool = Form(False, description="是否识别发票明细"),
    file: UploadFile = File(..., description="电子发票 PDF 文件"),
    db: AsyncSession = Depends(get_db),
):
    filename = file.filename or ""
    allowed_content_types = {"application/pdf", "application/octet-stream"}
    if file.content_type not in allowed_content_types and not filename.lower().endswith(
        ".pdf"
    ):
        raise HTTPException(status_code=400, detail="请上传 PDF 文件")

    pdf_bytes = await _read_upload_file_with_limit(file)
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="上传文件为空")

    try:
        result = await recognize_and_store_invoice_pdf(
            db,
            pdf_bytes,
            file_name=filename,
            include_details=include_details,
        )
    except DuplicateInvoiceError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"发票识别失败：{exc}") from exc

    return success_response(
        data=InvoiceRecognitionRecordResponse.model_validate(result).model_dump(
            mode="json"
        )
    )


async def _read_upload_file_with_limit(file: UploadFile) -> bytes:
    chunks: list[bytes] = []
    total_size = 0
    while True:
        chunk = await file.read(INVOICE_UPLOAD_CHUNK_SIZE)
        if not chunk:
            break
        total_size += len(chunk)
        if total_size > MAX_INVOICE_PDF_UPLOAD_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"PDF 文件不能超过 {settings.MAX_UPLOAD_SIZE_MB}MB",
            )
        chunks.append(chunk)

    return b"".join(chunks)


@router.get(
    "/invoices/recognition-records",
    summary="查询采购发票识别记录",
    description="查询已经保存到数据库的采购发票识别结果，支持按关键字、销售方和发票号码筛选。",
    response_model=InvoiceRecognitionRecordListResponse,
)
async def list_invoice_records(
    keyword: str | None = Query(None, description="文件名、发票号码或销售方关键词"),
    seller_name: str | None = Query(None, description="销售方名称"),
    invoice_number: str | None = Query(None, description="发票号码"),
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页条数"),
    db: AsyncSession = Depends(get_db),
):
    records, total = await list_invoice_recognition_records(
        db,
        keyword=keyword,
        seller_name=seller_name,
        invoice_number=invoice_number,
        page=page,
        page_size=page_size,
    )
    data = [
        InvoiceRecognitionRecordResponse.model_validate(record).model_dump(mode="json")
        for record in records
    ]
    return paginated_response(data, page, page_size, total)


@router.delete(
    "/invoices/recognition-records/{record_id}",
    summary="删除采购发票识别记录",
    description="软删除单条采购发票识别历史记录。",
    response_model=InvoiceRecognitionRecordDeleteResponse,
)
async def delete_invoice_record(
    record_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    deleted = await delete_invoice_recognition_record(db, record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="识别记录不存在或已删除")

    return success_response(
        data=InvoiceRecognitionRecordDeleteResult(
            success_count=1,
            fail_count=0,
        ).model_dump(mode="json"),
        message="识别记录删除成功",
    )


@router.post(
    "/invoices/recognition-records/batch-delete",
    summary="批量删除采购发票识别记录",
    description="软删除多条采购发票识别历史记录。",
    response_model=InvoiceRecognitionRecordDeleteResponse,
)
async def batch_delete_invoice_records(
    payload: InvoiceRecognitionRecordDeleteRequest,
    db: AsyncSession = Depends(get_db),
):
    deleted_count = await batch_delete_invoice_recognition_records(db, payload.ids)
    return success_response(
        data=InvoiceRecognitionRecordDeleteResult(
            success_count=deleted_count,
            fail_count=max(0, len(payload.ids) - deleted_count),
        ).model_dump(mode="json"),
        message="识别记录删除成功",
    )


@router.get(
    "/contracts/templates/{category}",
    summary="获取采购合同模板字段",
    description="返回指定合同分类的可填写字段，用于前端动态展示合同生成表单。",
    response_model=ContractTemplateMetadata,
)
async def get_contract_template(category: ContractCategory):
    metadata = get_contract_template_metadata(category)
    return success_response(data=metadata.model_dump(mode="json"))


@router.post(
    "/contracts/generate",
    summary="生成采购合同",
    description="根据合同分类、基础信息、供应商信息和明细行生成 Word 合同。",
)
async def create_contract(payload: ContractGenerateRequest):
    try:
        buffer, filename, media_type = generate_contract(payload)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    encoded_filename = quote(filename, safe="")
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename*=utf-8''{encoded_filename}"
        },
    )
