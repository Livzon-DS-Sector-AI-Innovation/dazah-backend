// quality module TypeScript types

export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
  meta?: {
    page?: number
    page_size?: number
    total?: number
  }
}

// ============ Enums ============

export enum MaterialCategory {
  RAW_MATERIAL = 'raw_material',       // 原料
  EXCIPIENT = 'excipient',            // 辅料
  PACKAGING_MATERIAL = 'packaging_material',  // 包装材料
  INTERMEDIATE = 'intermediate',      // 中间体
  FINISHED_PRODUCT = 'finished_product',    // 原料药成品
}

export enum Pharmacopeia {
  CHP = 'ChP',       // 中国药典
  USP = 'USP',       // 美国药典
  EP = 'EP',         // 欧洲药典
  BP = 'BP',         // 英国药典
  INTERNAL = 'internal',  // 企业内控
}

export enum StandardStatus {
  DRAFT = 'draft',           // 草稿
  TECH_REVIEW = 'tech_review',     // 技术部门审核
  QA_REVIEW = 'qa_review',         // QA审核
  APPROVED = 'approved',           // 已批准
  EFFECTIVE = 'effective',         // 已生效
  OBSOLETE = 'obsolete',           // 已作废
  REJECTED = 'rejected',           // 已驳回
}

export enum LimitType {
  UPPER_LIMIT = 'upper_limit',     // 上限
  LOWER_LIMIT = 'lower_limit',     // 下限
  RANGE = 'range',                 // 区间
  NOT_DETECTABLE = 'not_detectable', // 不得检出
}

export enum ItemCategory {
  PHYSICAL_CHEMICAL = 'physical_chemical',   // 理化
  RELATED_SUBSTANCES = 'related_substances',  // 有关物质
  RESIDUAL_SOLVENTS = 'residual_solvents',    // 残留溶剂
  MICROBIAL = 'microbial',                    // 微生物
}

export const MATERIAL_CATEGORY_OPTIONS = [
  { value: MaterialCategory.RAW_MATERIAL, label: '原料' },
  { value: MaterialCategory.EXCIPIENT, label: '辅料' },
  { value: MaterialCategory.PACKAGING_MATERIAL, label: '包装材料' },
  { value: MaterialCategory.INTERMEDIATE, label: '中间体' },
  { value: MaterialCategory.FINISHED_PRODUCT, label: '原料药成品' },
]

export const PHARMACOPEIA_OPTIONS = [
  { value: Pharmacopeia.CHP, label: 'ChP 中国药典' },
  { value: Pharmacopeia.USP, label: 'USP 美国药典' },
  { value: Pharmacopeia.EP, label: 'EP 欧洲药典' },
  { value: Pharmacopeia.BP, label: 'BP 英国药典' },
  { value: Pharmacopeia.INTERNAL, label: '企业内控' },
]

export const STANDARD_STATUS_OPTIONS = [
  { value: StandardStatus.DRAFT, label: '草稿', color: 'default' },
  { value: StandardStatus.TECH_REVIEW, label: '技术部门审核', color: 'processing' },
  { value: StandardStatus.QA_REVIEW, label: 'QA审核', color: 'processing' },
  { value: StandardStatus.APPROVED, label: '已批准', color: 'blue' },
  { value: StandardStatus.EFFECTIVE, label: '已生效', color: 'success' },
  { value: StandardStatus.OBSOLETE, label: '已作废', color: 'warning' },
  { value: StandardStatus.REJECTED, label: '已驳回', color: 'error' },
]

export const LIMIT_TYPE_OPTIONS = [
  { value: LimitType.UPPER_LIMIT, label: '上限' },
  { value: LimitType.LOWER_LIMIT, label: '下限' },
  { value: LimitType.RANGE, label: '区间' },
  { value: LimitType.NOT_DETECTABLE, label: '不得检出' },
]

export const ITEM_CATEGORY_OPTIONS = [
  { value: ItemCategory.PHYSICAL_CHEMICAL, label: '理化' },
  { value: ItemCategory.RELATED_SUBSTANCES, label: '有关物质' },
  { value: ItemCategory.RESIDUAL_SOLVENTS, label: '残留溶剂' },
  { value: ItemCategory.MICROBIAL, label: '微生物' },
]

// ============ InspectionStandard Types ============

export interface InspectionStandardItem {
  id: string
  standard_id: string
  item_no: number
  item_name: string
  test_method?: string
  instrument_code?: string
  reference_materials?: string
  limit_type: LimitType
  limit_value?: string
  item_category?: ItemCategory
  is_critical: boolean
  notes?: string
  created_at: string
  updated_at: string
}

export interface InspectionStandard {
  id: string
  standard_no: string
  material_code: string
  material_name?: string
  cas_no?: string
  material_category: MaterialCategory
  pharmacopeia?: Pharmacopeia
  version: string
  status: StandardStatus
  effective_date?: string
  obsolete_date?: string
  is_obsolete: boolean
  obsolete_reason?: string
  sop_no?: string
  attachment_urls?: string
  notes?: string
  source_version?: string
  items: InspectionStandardItem[]
  created_at: string
  updated_at: string
}

export interface InspectionStandardFormData {
  material_code: string
  material_name?: string
  cas_no?: string
  material_category: MaterialCategory
  pharmacopeia?: Pharmacopeia
  version?: string
  effective_date?: string
  obsolete_date?: string
  sop_no?: string
  attachment_urls?: string
  notes?: string
  items?: InspectionStandardItemFormData[]
}

export interface InspectionStandardItemFormData {
  item_no: number
  item_name: string
  test_method?: string
  instrument_code?: string
  reference_materials?: string
  limit_type: LimitType
  limit_value?: string
  item_category?: ItemCategory
  is_critical?: boolean
  notes?: string
}

export interface StandardCopyData {
  source_id: string
  new_version: string
}

export interface ObsoleteData {
  obsolete_reason: string
}

// ============ ApprovalRecord Types ============

export interface ApprovalRecord {
  id: string
  standard_id: string
  approval_level: number
  approval_status: string
  approver_role?: string
  approver_id?: string
  approver_name?: string
  approved_at?: string
  comments?: string
  created_at: string
  updated_at: string
}

// ============ Query Parameters ============

export interface StandardQueryParams {
  page?: number
  page_size?: number
  status?: StandardStatus
  material_code?: string
  material_name?: string
  material_category?: MaterialCategory
  pharmacopeia?: Pharmacopeia
  version?: string
  is_effective?: boolean
}