// warehouse module TypeScript types

/**
 * 试剂/标准品领用记录
 */
export interface ReagentUsage {
  id: string
  reagent_no: string
  reagent_name: string
  specification: string
  manufacturer: string
  batch_no: string
  quantity: number
  unit: string
  usage_date: string
  user_department: string
  user_name: string
  usage_reason: string
  status: 'draft' | 'submitted' | 'approved'
  created_at: string
  updated_at: string
}

/**
 * 试剂/标准品报废记录
 */
export interface ReagentScrap {
  id: string
  reagent_no: string
  reagent_name: string
  specification: string
  manufacturer: string
  batch_no: string
  quantity: number
  unit: string
  scrap_date: string
  scrap_reason: string
  scrap_type: 'expired' | 'damaged' | 'contaminated' | 'other'
  status: 'draft' | 'submitted' | 'approved'
  created_at: string
  updated_at: string
}

/**
 * AI 生成请求参数
 */
export interface AiGenRequest {
  bill_no: string
  user_input: string
  operator: string
}

/**
 * AI 生成响应
 */
export interface AiGenResponse {
  result: string
  bill_no: string
  operate_type: string
}

/**
 * 试剂台账
 */
export interface Reagent {
  id: string
  reagent_no: string
  reagent_name: string
  specification: string
  manufacturer: string
  CAS_no: string
  lot_no: string
  quantity: number
  unit: string
  location: string
  expiration_date: string
  storage_conditions: string
  status: 'available' | 'low_stock' | 'expired' | 'quarantine'
  created_at: string
  updated_at: string
}

/**
 * 领用事由标签映射
 */
export const usageReasonLabels: Record<string, string> = {
  routine: '常规检验',
  sampling: '取样检验',
  method_validation: '方法验证',
  stability: '稳定性考察',
  investigation: '偏差调查',
  other: '其他',
}

/**
 * 报废类型标签映射
 */
export const scrapTypeLabels: Record<string, string> = {
  expired: '过期报废',
  damaged: '破损报废',
  contaminated: '污染报废',
  other: '其他',
}

/**
 * 状态标签映射
 */
export const statusLabels: Record<string, string> = {
  draft: '草稿',
  submitted: '已提交',
  approved: '已审批',
  available: '库存充足',
  low_stock: '库存不足',
  expired: '已过期',
  quarantine: '待验',
}