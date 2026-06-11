"""Dossier Writer business workflows."""
import os
import shutil
import re
from pathlib import Path
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from docx import Document
# Removed invalid import
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from .models import ProductDossier, DossierTemplate, DossierChapter, ChapterAsset
from .repository import DossierRepository
from .m3_structure import M3_CHAPTERS, match_file_to_chapter
from .schemas import (
    ProductDossierCreate, ProductDossierUpdate,
    ChapterResponse, ChapterDetailResponse, AssetResponse,
)


class DossierService:
    """品种资料业务逻辑"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = DossierRepository(db)
        self.settings = get_settings()
        self.storage_root = Path(self.settings.STORAGE_ROOT) / "registration" / "dossier-writer"

    # ====== Product Dossier ======

    async def create_product_dossier(self, data: ProductDossierCreate) -> ProductDossier:
        """创建品种资料"""
        # 查重：检查是否已存在相同品种名称 + 生产商 + 无菌类型
        existing = await self.repo.check_duplicate(
            data.product_name, data.manufacturer, data.sterile_type
        )
        if existing:
            raise ValueError("该品种资料已存在，请勿重复创建")

        # 创建品种记录
        dossier = ProductDossier(
            product_name=data.product_name,
            sterile_type=data.sterile_type,
            manufacturer=data.manufacturer,
            template_original_product_name=data.template_original_product_name,
            template_original_manufacturer=data.template_original_manufacturer,
            status="draft",
            parse_status="pending",
        )
        dossier = await self.repo.create_product_dossier(dossier)

        # 创建存储目录
        dossier_id = str(dossier.id)
        paths = self._create_storage_dirs(dossier_id)
        
        dossier.source_templates_path = paths["source_templates"]
        dossier.working_path = paths["working"]
        dossier.assets_path = paths["assets"]
        dossier.outputs_path = paths["outputs"]
        
        # 创建 M3 标准目录树
        await self._create_m3_chapters(dossier.id)
        
        await self.db.commit()
        await self.db.refresh(dossier)
        return dossier

    async def get_product_dossier(self, dossier_id: UUID) -> Optional[ProductDossier]:
        """获取品种资料详情"""
        dossier = await self.repo.get_product_dossier(dossier_id)
        if dossier:
            chapter_count = await self.repo.count_chapters(dossier_id)
            dossier.chapter_count = chapter_count
        return dossier

    async def list_product_dossiers(
        self, skip: int = 0, limit: int = 100
    ) -> tuple[List[ProductDossier], int]:
        """获取品种资料列表"""
        items, total = await self.repo.list_product_dossiers(skip, limit)
        # 填充章节数量
        for item in items:
            item.chapter_count = await self.repo.count_chapters(item.id)
        return items, total

    async def update_product_dossier(
        self, dossier_id: UUID, data: ProductDossierUpdate
    ) -> Optional[ProductDossier]:
        """更新品种资料"""
        update_data = data.model_dump(exclude_unset=True)
        if update_data:
            dossier = await self.repo.update_product_dossier(dossier_id, **update_data)
            await self.db.commit()
            return dossier
        return await self.repo.get_product_dossier(dossier_id)

    async def delete_product_dossier(self, dossier_id: UUID) -> bool:
        """删除品种资料"""
        # 软删除数据库记录
        success = await self.repo.delete_product_dossier(dossier_id)
        if success:
            # 删除物理文件
            self._delete_storage_dirs(str(dossier_id))
            await self.db.commit()
        return success

    # ====== Template Management ======

    async def save_template_file(
        self, dossier_id: UUID, filename: str, file_content: bytes
    ) -> DossierTemplate:
        """保存模板文件"""
        dossier = await self.repo.get_product_dossier(dossier_id)
        if not dossier:
            raise ValueError(f"品种资料不存在: {dossier_id}")

        # 保存文件
        source_dir = Path(dossier.source_templates_path)
        source_dir.mkdir(parents=True, exist_ok=True)
        file_path = source_dir / filename
        file_path.write_bytes(file_content)

        # 创建记录
        template = DossierTemplate(
            product_dossier_id=dossier_id,
            original_filename=filename,
            file_path=str(file_path),
            file_size=len(file_content),
        )
        template = await self.repo.create_template(template)
        await self.db.commit()
        return template

    # ====== Template Parsing ======

    async def parse_templates(self, dossier_id: UUID) -> Dict[str, Any]:
        """解析模板并匹配到 M3 章节"""
        dossier = await self.repo.get_product_dossier(dossier_id)
        if not dossier:
            return {"success": False, "message": "品种资料不存在", "error": "NOT_FOUND"}

        try:
            # 更新状态
            await self.repo.update_product_dossier(
                dossier_id, parse_status="parsing", parse_error=None
            )
            await self.db.commit()

            # 获取模板文件
            templates = await self.repo.list_templates(dossier_id)
            if not templates:
                raise ValueError("没有上传模板文件")

            # 获取现有 M3 章节
            chapters = await self.repo.get_chapter_tree(dossier_id)
            if not chapters:
                # 如果没有章节，创建 M3 标准目录
                await self._create_m3_chapters(dossier_id)
                await self.db.commit()
                chapters = await self.repo.get_chapter_tree(dossier_id)

            # 匹配模板到章节
            matched_count = 0
            for template in templates:
                matched_code = match_file_to_chapter(template.original_filename)
                if matched_code:
                    # 找到对应章节
                    matched_chapter = None
                    for ch in chapters:
                        if ch.chapter_code == matched_code:
                            matched_chapter = ch
                            break
                    
                    if matched_chapter:
                        # 创建 working copy
                        await self._create_working_copy_for_chapter(dossier, template, matched_chapter)
                        matched_count += 1

            # 更新状态
            await self.repo.update_product_dossier(
                dossier_id, 
                parse_status="parsed", 
                status="active"
            )
            await self.db.commit()

            return {
                "success": True,
                "message": f"解析完成，共上传 {len(templates)} 个模板文件，成功匹配 {matched_count} 个",
                "chapter_count": len(chapters),
                "template_count": len(templates),
                "matched_count": matched_count,
            }

        except Exception as e:
            await self.repo.update_product_dossier(
                dossier_id, parse_status="failed", parse_error=str(e)
            )
            await self.db.commit()

            return {
                "success": False,
                "message": f"解析失败: {str(e)}",
                "error": str(e),
            }

    async def _parse_docx_template(
        self, dossier: ProductDossier, template: DossierTemplate
    ) -> List[DossierChapter]:
        """解析单个 DOCX 模板"""
        source_path = Path(template.file_path)
        working_dir = Path(dossier.working_path)
        working_dir.mkdir(parents=True, exist_ok=True)

        # 创建 working copy
        working_filename = self._generate_working_filename(
            template.original_filename, dossier
        )
        working_path = working_dir / working_filename
        shutil.copy2(source_path, working_path)

        # 执行基础信息替换
        self._replace_basic_info(working_path, dossier)

        # 解析章节结构
        doc = Document(str(working_path))
        chapters = []
        sort_order = 0

        for para_idx, para in enumerate(doc.paragraphs):
            style_name = para.style.name if para.style else ""
            text = para.text.strip()
            
            if not text:
                continue

            # 判断是否是标题
            level = self._detect_heading_level(style_name, text)
            if level > 0:
                chapter_code = self._extract_chapter_code(text)
                chapter_title = self._clean_chapter_title(text)
                
                chapter = DossierChapter(
                    product_dossier_id=dossier.id,
                    chapter_code=chapter_code,
                    chapter_title=chapter_title,
                    level=level,
                    sort_order=sort_order,
                    source_file=template.original_filename,
                    working_file=working_filename,
                    paragraph_start=para_idx,
                    paragraph_end=para_idx,
                    has_content=True,
                )
                chapters.append(chapter)
                sort_order += 1

        return chapters

    def _detect_heading_level(self, style_name: str, text: str) -> int:
        """检测标题层级"""
        # 基于样式名称
        style_lower = style_name.lower()
        if "heading 1" in style_lower or style_lower == "heading1":
            return 1
        if "heading 2" in style_lower or style_lower == "heading2":
            return 2
        if "heading 3" in style_lower or style_lower == "heading3":
            return 3
        if "heading 4" in style_lower or style_lower == "heading4":
            return 4
        if "heading" in style_lower:
            return 2  # 默认二级

        # 基于编号规则（如 3.2.S.1.1）
        if re.match(r'^\d+(\.\d+)*\s', text):
            parts = text.split()[0].split('.')
            return min(len(parts), 4)

        return 0  # 不是标题

    def _extract_chapter_code(self, text: str) -> Optional[str]:
        """提取章节编号"""
        match = re.match(r'^(\d+(?:\.\d+)*|[A-Z](?:\.\d+)*)', text)
        if match:
            return match.group(1)
        return None

    def _clean_chapter_title(self, text: str) -> str:
        """清理章节标题"""
        # 移除编号前缀
        text = re.sub(r'^[\d\.]+[A-Z\.]*\s*', '', text)
        return text.strip()

    def _generate_working_filename(
        self, original_filename: str, dossier: ProductDossier
    ) -> str:
        """生成工作副本文件名"""
        name, ext = os.path.splitext(original_filename)
        
        # 替换旧品种名
        if dossier.template_original_product_name:
            name = name.replace(
                dossier.template_original_product_name,
                dossier.product_name
            )
        
        return f"{name}_working{ext}"

    def _replace_basic_info(self, file_path: Path, dossier: ProductDossier) -> None:
        """替换基础信息"""
        doc = Document(str(file_path))

        replacements = {}
        
        # 品种名称替换
        if dossier.template_original_product_name:
            replacements[dossier.template_original_product_name] = dossier.product_name
        
        # 生产商替换
        if dossier.template_original_manufacturer:
            replacements[dossier.template_original_manufacturer] = dossier.manufacturer

        # 无菌类型替换（常见模式）
        sterile_map = {
            "无菌": dossier.sterile_type if "无菌" in dossier.sterile_type else "无菌",
            "非无菌": dossier.sterile_type if "非无菌" in dossier.sterile_type else "非无菌",
        }
        for old, new in sterile_map.items():
            if old != new:
                replacements[old] = new

        if not replacements:
            doc.save(str(file_path))
            return

        # 替换段落
        for para in doc.paragraphs:
            self._replace_in_paragraph(para, replacements)

        # 替换表格
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        self._replace_in_paragraph(para, replacements)

        # 替换页眉页脚
        for section in doc.sections:
            for header in [section.header, section.first_page_header, section.even_page_header]:
                try:
                    for para in header.paragraphs:
                        self._replace_in_paragraph(para, replacements)
                except Exception:
                    pass
            
            for footer in [section.footer, section.first_page_footer, section.even_page_footer]:
                try:
                    for para in footer.paragraphs:
                        self._replace_in_paragraph(para, replacements)
                except Exception:
                    pass

        doc.save(str(file_path))

    def _replace_in_paragraph(self, para, replacements: Dict[str, str]) -> None:
        """替换段落中的文本"""
        for run in para.runs:
            for old_text, new_text in replacements.items():
                if old_text in run.text:
                    run.text = run.text.replace(old_text, new_text)

    # ====== Chapter Management ======

    async def get_chapter_tree(self, dossier_id: UUID) -> List[ChapterResponse]:
        """获取章节树"""
        chapters = await self.repo.get_chapter_tree(dossier_id)
        return self._build_chapter_tree(chapters)

    def _build_chapter_tree(self, chapters: List[DossierChapter]) -> List[ChapterResponse]:
        """构建章节树结构"""
        chapter_map: Dict[Optional[UUID], List[DossierChapter]] = {}
        
        for chapter in chapters:
            parent_id = chapter.parent_id
            if parent_id not in chapter_map:
                chapter_map[parent_id] = []
            chapter_map[parent_id].append(chapter)

        def build_node(chapter: DossierChapter) -> ChapterResponse:
            children = chapter_map.get(chapter.id, [])
            return ChapterResponse(
                id=chapter.id,
                parent_id=chapter.parent_id,
                chapter_code=chapter.chapter_code,
                chapter_title=chapter.chapter_title,
                level=chapter.level,
                sort_order=chapter.sort_order,
                has_content=chapter.has_content,
                has_assets=chapter.has_assets,
                asset_count=len(chapter.assets) if chapter.assets else 0,
                source_file=chapter.source_file,
                working_file=chapter.working_file,
                children=[build_node(c) for c in children],
            )

        # 根节点是 parent_id 为 None 的章节
        root_chapters = chapter_map.get(None, [])
        return [build_node(c) for c in root_chapters]

    async def get_chapter_detail(self, chapter_id: UUID) -> Optional[ChapterDetailResponse]:
        """获取章节详情"""
        chapter = await self.repo.get_chapter(chapter_id)
        if not chapter:
            return None
        
        assets = [
            AssetResponse(
                id=a.id,
                original_filename=a.original_filename,
                file_type=a.file_type,
                file_size=a.file_size,
                uploaded_at=a.uploaded_at,
            )
            for a in (chapter.assets or [])
        ]
        
        return ChapterDetailResponse(
            id=chapter.id,
            chapter_code=chapter.chapter_code,
            chapter_title=chapter.chapter_title,
            level=chapter.level,
            has_content=chapter.has_content,
            has_assets=chapter.has_assets,
            source_file=chapter.source_file,
            working_file=chapter.working_file,
            assets=assets,
        )

    # ====== Asset Management ======

    async def upload_chapter_asset(
        self, chapter_id: UUID, filename: str, file_content: bytes
    ) -> ChapterAsset:
        """上传章节素材"""
        chapter = await self.repo.get_chapter(chapter_id)
        if not chapter:
            raise ValueError(f"章节不存在: {chapter_id}")

        dossier = await self.repo.get_product_dossier(chapter.product_dossier_id)
        if not dossier:
            raise ValueError("品种资料不存在")

        # 保存文件
        assets_dir = Path(dossier.assets_path) / str(chapter_id)
        assets_dir.mkdir(parents=True, exist_ok=True)
        file_path = assets_dir / filename
        file_path.write_bytes(file_content)

        # 获取文件类型
        file_type = Path(filename).suffix.lower().lstrip('.')

        # 创建记录
        asset = ChapterAsset(
            chapter_id=chapter_id,
            original_filename=filename,
            file_path=str(file_path),
            file_type=file_type,
            file_size=len(file_content),
        )
        asset = await self.repo.create_asset(asset)

        # 更新章节状态
        await self.repo.update_chapter(chapter_id, has_assets=True)
        await self.db.commit()
        
        return asset

    async def list_chapter_assets(self, chapter_id: UUID) -> List[ChapterAsset]:
        """获取章节素材列表"""
        return await self.repo.list_assets(chapter_id)

    async def delete_asset(self, asset_id: UUID) -> bool:
        """删除素材"""
        asset = await self.repo.get_asset(asset_id)
        if not asset:
            return False

        # 删除物理文件
        file_path = Path(asset.file_path)
        if file_path.exists():
            file_path.unlink()

        # 删除记录
        await self.repo.delete_asset(asset_id)
        
        # 更新章节状态
        remaining = await self.repo.count_assets(asset.chapter_id)
        if remaining == 0:
            await self.repo.update_chapter(asset.chapter_id, has_assets=False)
        
        await self.db.commit()
        return True

    # ====== Export ======

    async def export_dossier(
        self, dossier_id: UUID, chapter_ids: Optional[List[UUID]] = None
    ) -> Dict[str, Any]:
        """导出品种资料"""
        dossier = await self.repo.get_product_dossier(dossier_id)
        if not dossier:
            return {"success": False, "message": "品种资料不存在"}

        working_dir = Path(dossier.working_path)
        outputs_dir = Path(dossier.outputs_path)
        outputs_dir.mkdir(parents=True, exist_ok=True)

        # 生成导出文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_filename = f"{dossier.product_name}_申报资料_{timestamp}.docx"
        export_path = outputs_dir / export_filename

        # 简单实现：复制 working copy 作为导出
        # TODO: 后续实现合并多个章节、应用素材内容等
        if chapter_ids:
            # 导出指定章节（简化处理）
            chapters = await self.repo.get_chapter_tree(dossier_id)
            source_files = set()
            for chapter in chapters:
                if chapter.id in chapter_ids and chapter.working_file:
                    source_files.add(chapter.working_file)
            
            if len(source_files) == 1:
                source_file = working_dir / list(source_files)[0]
                if source_file.exists():
                    shutil.copy2(source_file, export_path)
            else:
                # 多文件合并（简化：复制第一个）
                for sf in source_files:
                    source_file = working_dir / sf
                    if source_file.exists():
                        shutil.copy2(source_file, export_path)
                        break
        else:
            # 导出全部（复制第一个 working 文件）
            working_files = list(working_dir.glob("*.docx"))
            if working_files:
                shutil.copy2(working_files[0], export_path)

        if export_path.exists():
            return {
                "success": True,
                "message": "导出成功",
                "file_path": str(export_path),
                "filename": export_filename,
            }
        else:
            return {"success": False, "message": "导出失败：无可用文件"}

    # ====== Storage Helpers ======

    def _create_storage_dirs(self, dossier_id: str) -> Dict[str, str]:
        """创建存储目录"""
        base = self.storage_root / "products" / dossier_id
        dirs = {
            "source_templates": base / "source_templates",
            "working": base / "working",
            "assets": base / "assets",
            "outputs": base / "outputs",
        }
        for d in dirs.values():
            d.mkdir(parents=True, exist_ok=True)
        return {k: str(v) for k, v in dirs.items()}

    def _delete_storage_dirs(self, dossier_id: str) -> None:
        """删除存储目录"""
        base = self.storage_root / "products" / dossier_id
        if base.exists():
            shutil.rmtree(base)

    async def _create_m3_chapters(self, dossier_id: UUID) -> None:
        """创建 M3 标准目录结构"""
        code_to_id: Dict[str, UUID] = {}
        
        # 按层级顺序创建章节
        for ch in sorted(M3_CHAPTERS, key=lambda x: x["level"]):
            parent_id = code_to_id.get(ch["parent_code"]) if ch["parent_code"] else None
            
            chapter = DossierChapter(
                product_dossier_id=dossier_id,
                parent_id=parent_id,
                chapter_code=ch["code"],
                chapter_title=ch["title"],
                level=ch["level"],
                sort_order=0,
                has_content=False,
                has_assets=False,
            )
            chapter = await self.repo.create_chapter(chapter)
            code_to_id[ch["code"]] = chapter.id

    async def _create_working_copy_for_chapter(
        self, dossier: ProductDossier, template: DossierTemplate, chapter: DossierChapter
    ) -> None:
        """为章节创建 working copy"""
        source_path = Path(template.file_path)
        working_dir = Path(dossier.working_path)
        working_dir.mkdir(parents=True, exist_ok=True)

        # 生成 working copy 文件名
        working_filename = f"{chapter.chapter_code.replace('.', '_')}_{source_path.name}"
        working_path = working_dir / working_filename

        # 复制文件
        shutil.copy2(source_path, working_path)

        # 执行基础信息替换
        self._replace_basic_info(working_path, dossier)

        # 更新章节信息
        await self.repo.update_chapter(
            chapter.id,
            source_file=template.original_filename,
            working_file=working_filename,
            has_content=True,
        )


    async def get_chapter_preview(self, chapter_id: UUID) -> Dict[str, Any]:
        """获取章节预览内容（从 working copy 提取）"""
        chapter = await self.repo.get_chapter(chapter_id)
        if not chapter:
            return {"success": False, "message": "章节不存在"}
        
        if not chapter.working_file:
            return {"success": False, "message": "章节无工作副本"}
        
        dossier = await self.repo.get_product_dossier(chapter.product_dossier_id)
        if not dossier:
            return {"success": False, "message": "品种不存在"}
        
        working_path = Path(dossier.working_path) / chapter.working_file
        if not working_path.exists():
            return {"success": False, "message": "工作副本文件不存在"}
        
        try:
            doc = Document(str(working_path))
            
            # 提取文本内容
            paragraphs = []
            for para in doc.paragraphs:
                if para.text.strip():
                    paragraphs.append({
                        "text": para.text,
                        "style": para.style.name if para.style else "Normal",
                    })
            
            # 提取表格
            tables = []
            for table in doc.tables:
                rows = []
                for row in table.rows:
                    cells = [cell.text.strip() for cell in row.cells]
                    rows.append(cells)
                tables.append(rows)
            
            return {
                "success": True,
                "chapter_code": chapter.chapter_code,
                "chapter_title": chapter.chapter_title,
                "paragraphs": paragraphs,
                "tables": tables,
            }
        except Exception as e:
            return {"success": False, "message": f"预览失败: {str(e)}"}

    async def match_assets_to_chapters(self, dossier_id: UUID) -> Dict[str, Any]:
        """智能匹配素材到章节"""
        dossier = await self.repo.get_product_dossier(dossier_id)
        if not dossier:
            return {"success": False, "message": "品种不存在", "matched_count": 0, "unmatched_files": []}
        
        # 获取所有模板文件
        templates = await self.repo.list_templates(dossier_id)
        if not templates:
            return {"success": False, "message": "无模板文件", "matched_count": 0, "unmatched_files": []}
        
        # 获取所有章节（扁平列表）
        chapters = await self.repo.get_chapter_tree(dossier_id)
        
        matched_count = 0
        unmatched_files = []
        
        for template in templates:
            filename = template.original_filename
            
            # 尝试匹配章节
            matched_code = match_file_to_chapter(filename)
            
            if matched_code:
                # 找到对应章节
                matched_chapter = None
                for ch in chapters:
                    if ch.chapter_code == matched_code:
                        matched_chapter = ch
                        break
                
                if matched_chapter:
                    # 创建 working copy
                    await self._create_working_copy_for_chapter(dossier, template, matched_chapter)
                    matched_count += 1
            else:
                unmatched_files.append(filename)
        
        await self.db.commit()
        
        return {
            "success": True,
            "message": f"匹配完成：{matched_count} 个文件已匹配，{len(unmatched_files)} 个未匹配",
            "matched_count": matched_count,
            "unmatched_files": unmatched_files,
        }
