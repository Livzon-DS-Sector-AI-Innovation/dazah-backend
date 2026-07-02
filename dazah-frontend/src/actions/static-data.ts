'use server'

/**
 * 业务静态数据模块 Server Actions
 * 所有前端 API 调用都通过这里
 */

import {
  ApiResponse,
  PageParams,
  // 字典
  DictOption,
  // 预警
  WarningsResponse,
  WarningItem,
} from '@/types/static-data'

// 注意：Server Action 在服务器端执行
// 开发环境：后端在 8004，前端 .env.local 指向 8004（本地开发用）
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8004/api/v1'
const PREFIX = '/quality/static-data'

async function api<T = any>(
  path: string,
  options: RequestInit = {},
): Promise<ApiResponse<T>> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options.headers },
  })
  const data = await res.json()
  // 后端 code: 200=成功，其他=业务错误（如400验证失败/404不存在）
  // 注意：即使 HTTP 200，若 code != 200 也说明请求处理出了问题
  if (!res.ok || (data.code !== 200 && data.code !== 0)) {
    throw new Error(data.message || `请求失败(code: ${data.code}, HTTP ${res.status})`)
  }
  return data
}

// ========== 字典接口 ==========

export async function getDictEquipmentCategory() {
  return api<DictOption[]>(`${PREFIX}/dict/equipment-category`)
}

export async function getDictEquipmentStatus() {
  return api<DictOption[]>(`${PREFIX}/dict/equipment-status`)
}

export async function getDictVerifyStatus() {
  return api<DictOption[]>(`${PREFIX}/dict/verify-status`)
}

export async function getDictChromColumnStatus() {
  return api<DictOption[]>(`${PREFIX}/dict/chrom-column-status`)
}

export async function getDictMediumType() {
  return api<DictOption[]>(`${PREFIX}/dict/medium-type`)
}

export async function getDictReagentPurity() {
  return api<DictOption[]>(`${PREFIX}/dict/reagent-purity`)
}

export async function getDictDangerType() {
  return api<DictOption[]>(`${PREFIX}/dict/danger-type`)
}

export async function getDictStdType() {
  return api<DictOption[]>(`${PREFIX}/dict/std-type`)
}

export async function getDictMaterialType() {
  return api<DictOption[]>(`${PREFIX}/dict/material-type`)
}

export async function getDictStandardSource() {
  return api<DictOption[]>(`${PREFIX}/dict/standard-source`)
}

export async function getDictLimitType() {
  return api<DictOption[]>(`${PREFIX}/dict/limit-type`)
}

export async function getDictTestItemCategory() {
  return api<DictOption[]>(`${PREFIX}/dict/test-item-category`)
}

export async function getDictUnitType() {
  return api<DictOption[]>(`${PREFIX}/dict/unit-type`)
}

export async function getDictLab() {
  return api<DictOption[]>(`${PREFIX}/dict/lab`)
}

// ========== 贮存条件字典 ==========

export async function listStorageCondition(params: PageParams & { cond_code?: string; cond_name?: string; status?: number }) {
  const qs = new URLSearchParams()
  if (params.page) qs.set('page', String(params.page))
  if (params.page_size) qs.set('page_size', String(params.page_size))
  if (params.cond_code) qs.set('cond_code', params.cond_code)
  if (params.cond_name) qs.set('cond_name', params.cond_name)
  if (params.status !== undefined) qs.set('status', String(params.status))
  return api(`${PREFIX}/storage-condition?${qs}`)
}

export async function getStorageConditionOptions() {
  return api(`${PREFIX}/storage-condition/options`)
}

export async function getStorageCondition(id: number) {
  return api(`${PREFIX}/storage-condition/${id}`)
}

export async function createStorageCondition(data: any) {
  return api(`${PREFIX}/storage-condition`, { method: 'POST', body: JSON.stringify(data) })
}

export async function updateStorageCondition(id: number, data: any) {
  return api(`${PREFIX}/storage-condition/${id}`, { method: 'PUT', body: JSON.stringify(data) })
}

export async function deleteStorageCondition(id: number) {
  return api(`${PREFIX}/storage-condition/${id}`, { method: 'DELETE' })
}

export async function toggleStorageConditionStatus(id: number) {
  return api(`${PREFIX}/storage-condition/${id}/toggle-status`, { method: 'POST' })
}

// ========== 计量单位字典 ==========

export async function listUnit(params: PageParams & { unit_code?: string; unit_name?: string; unit_type?: string; status?: number }) {
  const qs = new URLSearchParams()
  if (params.page) qs.set('page', String(params.page))
  if (params.page_size) qs.set('page_size', String(params.page_size))
  if (params.unit_code) qs.set('unit_code', params.unit_code)
  if (params.unit_name) qs.set('unit_name', params.unit_name)
  if (params.unit_type) qs.set('unit_type', params.unit_type)
  if (params.status !== undefined) qs.set('status', String(params.status))
  return api(`${PREFIX}/unit?${qs}`)
}

export async function getUnitOptions() {
  return api(`${PREFIX}/unit/options`)
}

export async function getUnit(id: number) {
  return api(`${PREFIX}/unit/${id}`)
}

export async function createUnit(data: any) {
  return api(`${PREFIX}/unit`, { method: 'POST', body: JSON.stringify(data) })
}

export async function updateUnit(id: number, data: any) {
  return api(`${PREFIX}/unit/${id}`, { method: 'PUT', body: JSON.stringify(data) })
}

export async function deleteUnit(id: number) {
  return api(`${PREFIX}/unit/${id}`, { method: 'DELETE' })
}

// ========== 检验项目字典 ==========

export async function listTestItem(params: PageParams & { item_code?: string; item_name?: string; item_category?: string; status?: number }) {
  const qs = new URLSearchParams()
  if (params.page) qs.set('page', String(params.page))
  if (params.page_size) qs.set('page_size', String(params.page_size))
  if (params.item_code) qs.set('item_code', params.item_code)
  if (params.item_name) qs.set('item_name', params.item_name)
  if (params.item_category) qs.set('item_category', params.item_category)
  if (params.status !== undefined) qs.set('status', String(params.status))
  return api(`${PREFIX}/test-item?${qs}`)
}

export async function getTestItemOptions() {
  return api(`${PREFIX}/test-item/options`)
}

export async function getTestItem(id: number) {
  return api(`${PREFIX}/test-item/${id}`)
}

export async function createTestItem(data: any) {
  return api(`${PREFIX}/test-item`, { method: 'POST', body: JSON.stringify(data) })
}

export async function updateTestItem(id: number, data: any) {
  return api(`${PREFIX}/test-item/${id}`, { method: 'PUT', body: JSON.stringify(data) })
}

export async function deleteTestItem(id: number) {
  return api(`${PREFIX}/test-item/${id}`, { method: 'DELETE' })
}

// ========== 检测设备台账 ==========

export async function listEquipment(params: PageParams & { eq_code?: string; eq_name?: string; eq_category?: string; eq_status?: number; verify_status?: string }) {
  const qs = new URLSearchParams()
  if (params.page) qs.set('page', String(params.page))
  if (params.page_size) qs.set('page_size', String(params.page_size))
  if (params.eq_code) qs.set('eq_code', params.eq_code)
  if (params.eq_name) qs.set('eq_name', params.eq_name)
  if (params.eq_category) qs.set('eq_category', params.eq_category)
  if (params.eq_status !== undefined) qs.set('eq_status', String(params.eq_status))
  if (params.verify_status) qs.set('verify_status', params.verify_status)
  return api(`${PREFIX}/equipment?${qs}`)
}

export async function getEquipment(id: number) {
  return api(`${PREFIX}/equipment/${id}`)
}

export async function createEquipment(data: any) {
  return api(`${PREFIX}/equipment`, { method: 'POST', body: JSON.stringify(data) })
}

export async function updateEquipment(id: number, data: any) {
  return api(`${PREFIX}/equipment/${id}`, { method: 'PUT', body: JSON.stringify(data) })
}

export async function deleteEquipment(id: number) {
  return api(`${PREFIX}/equipment/${id}`, { method: 'DELETE' })
}

// ========== 色谱柱管理 ==========

export async function listChromColumn(params: PageParams & { col_code?: string; col_type?: string; col_status?: number }) {
  const qs = new URLSearchParams()
  if (params.page) qs.set('page', String(params.page))
  if (params.page_size) qs.set('page_size', String(params.page_size))
  if (params.col_code) qs.set('col_code', params.col_code)
  if (params.col_type) qs.set('col_type', params.col_type)
  if (params.col_status !== undefined) qs.set('col_status', String(params.col_status))
  return api(`${PREFIX}/chrom-column?${qs}`)
}

export async function getChromColumn(id: number) {
  return api(`${PREFIX}/chrom-column/${id}`)
}

export async function createChromColumn(data: any) {
  return api(`${PREFIX}/chrom-column`, { method: 'POST', body: JSON.stringify(data) })
}

export async function updateChromColumn(id: number, data: any) {
  return api(`${PREFIX}/chrom-column/${id}`, { method: 'PUT', body: JSON.stringify(data) })
}

export async function deleteChromColumn(id: number) {
  return api(`${PREFIX}/chrom-column/${id}`, { method: 'DELETE' })
}

export async function incrementChromColumnUsage(id: number) {
  return api(`${PREFIX}/chrom-column/${id}/increment-usage`, { method: 'POST' })
}

// ========== 培养基管理 ==========

export async function listMedium(params: PageParams & { medium_code?: string; medium_name?: string; medium_type?: string; status?: number }) {
  const qs = new URLSearchParams()
  if (params.page) qs.set('page', String(params.page))
  if (params.page_size) qs.set('page_size', String(params.page_size))
  if (params.medium_code) qs.set('medium_code', params.medium_code)
  if (params.medium_name) qs.set('medium_name', params.medium_name)
  if (params.medium_type) qs.set('medium_type', params.medium_type)
  if (params.status !== undefined) qs.set('status', String(params.status))
  return api(`${PREFIX}/medium?${qs}`)
}

export async function getMedium(id: number) {
  return api(`${PREFIX}/medium/${id}`)
}

export async function createMedium(data: any) {
  return api(`${PREFIX}/medium`, { method: 'POST', body: JSON.stringify(data) })
}

export async function updateMedium(id: number, data: any) {
  return api(`${PREFIX}/medium/${id}`, { method: 'PUT', body: JSON.stringify(data) })
}

export async function deleteMedium(id: number) {
  return api(`${PREFIX}/medium/${id}`, { method: 'DELETE' })
}

// ========== 试剂管理 ==========

export async function listReagent(params: PageParams & { reagent_code?: string; reagent_name?: string; danger_type?: string; status?: number }) {
  const qs = new URLSearchParams()
  if (params.page) qs.set('page', String(params.page))
  if (params.page_size) qs.set('page_size', String(params.page_size))
  if (params.reagent_code) qs.set('reagent_code', params.reagent_code)
  if (params.reagent_name) qs.set('reagent_name', params.reagent_name)
  if (params.danger_type) qs.set('danger_type', params.danger_type)
  if (params.status !== undefined) qs.set('status', String(params.status))
  return api(`${PREFIX}/reagent?${qs}`)
}

export async function getReagent(id: number) {
  return api(`${PREFIX}/reagent/${id}`)
}

export async function createReagent(data: any) {
  return api(`${PREFIX}/reagent`, { method: 'POST', body: JSON.stringify(data) })
}

export async function updateReagent(id: number, data: any) {
  return api(`${PREFIX}/reagent/${id}`, { method: 'PUT', body: JSON.stringify(data) })
}

export async function deleteReagent(id: number) {
  return api(`${PREFIX}/reagent/${id}`, { method: 'DELETE' })
}

// ========== 标准物质管理 ==========

export async function listStandardMaterial(params: PageParams & { std_code?: string; std_name?: string; std_type?: string; status?: number }) {
  const qs = new URLSearchParams()
  if (params.page) qs.set('page', String(params.page))
  if (params.page_size) qs.set('page_size', String(params.page_size))
  if (params.std_code) qs.set('std_code', params.std_code)
  if (params.std_name) qs.set('std_name', params.std_name)
  if (params.std_type) qs.set('std_type', params.std_type)
  if (params.status !== undefined) qs.set('status', String(params.status))
  return api(`${PREFIX}/standard-material?${qs}`)
}

export async function getStandardMaterial(id: number) {
  return api(`${PREFIX}/standard-material/${id}`)
}

export async function createStandardMaterial(data: any) {
  return api(`${PREFIX}/standard-material`, { method: 'POST', body: JSON.stringify(data) })
}

export async function updateStandardMaterial(id: number, data: any) {
  return api(`${PREFIX}/standard-material/${id}`, { method: 'PUT', body: JSON.stringify(data) })
}

export async function deleteStandardMaterial(id: number) {
  return api(`${PREFIX}/standard-material/${id}`, { method: 'DELETE' })
}

// ========== 物料质量标准 ==========

export async function listMaterialStandard(params: PageParams & { material_code?: string; material_name?: string; material_type?: string; status?: number }) {
  const qs = new URLSearchParams()
  if (params.page) qs.set('page', String(params.page))
  if (params.page_size) qs.set('page_size', String(params.page_size))
  if (params.material_code) qs.set('material_code', params.material_code)
  if (params.material_name) qs.set('material_name', params.material_name)
  if (params.material_type) qs.set('material_type', params.material_type)
  if (params.status !== undefined) qs.set('status', String(params.status))
  return api(`${PREFIX}/material-standard?${qs}`)
}

export async function getMaterialStandard(id: number) {
  return api(`${PREFIX}/material-standard/${id}`)
}

export async function createMaterialStandard(data: any) {
  return api(`${PREFIX}/material-standard`, { method: 'POST', body: JSON.stringify(data) })
}

export async function updateMaterialStandard(id: number, data: any) {
  return api(`${PREFIX}/material-standard/${id}`, { method: 'PUT', body: JSON.stringify(data) })
}

export async function deleteMaterialStandard(id: number) {
  return api(`${PREFIX}/material-standard/${id}`, { method: 'DELETE' })
}

// ========== 产品质量标准 ==========

export async function listProductStandard(params: PageParams & { product_code?: string; product_name?: string; status?: number }) {
  const qs = new URLSearchParams()
  if (params.page) qs.set('page', String(params.page))
  if (params.page_size) qs.set('page_size', String(params.page_size))
  if (params.product_code) qs.set('product_code', params.product_code)
  if (params.product_name) qs.set('product_name', params.product_name)
  if (params.status !== undefined) qs.set('status', String(params.status))
  return api(`${PREFIX}/product-standard?${qs}`)
}

export async function getProductStandard(id: number) {
  return api(`${PREFIX}/product-standard/${id}`)
}

export async function createProductStandard(data: any) {
  return api(`${PREFIX}/product-standard`, { method: 'POST', body: JSON.stringify(data) })
}

export async function updateProductStandard(id: number, data: any) {
  return api(`${PREFIX}/product-standard/${id}`, { method: 'PUT', body: JSON.stringify(data) })
}

export async function deleteProductStandard(id: number) {
  return api(`${PREFIX}/product-standard/${id}`, { method: 'DELETE' })
}

// ========== 液相色谱对照品 ==========

export async function getHplcReference(id: number) {
  return api(`${PREFIX}/hplc-reference/${id}`)
}

export async function createHplcReference(data: any) {
  return api(`${PREFIX}/hplc-reference`, { method: 'POST', body: JSON.stringify(data) })
}

export async function updateHplcReference(id: number, data: any) {
  return api(`${PREFIX}/hplc-reference/${id}`, { method: 'PUT', body: JSON.stringify(data) })
}

export async function deleteHplcReference(id: number) {
  return api(`${PREFIX}/hplc-reference/${id}`, { method: 'DELETE' })
}

// ========== 预警 ==========

export async function getWarnings(days = 30): Promise<ApiResponse<WarningsResponse>> {
  return api(`${PREFIX}/warnings?days=${days}`)
}

// ========== 审计日志 ==========

export interface AuditLogItem {
  id: number
  module_type: string
  record_id: number
  record_code: string | null
  operate_type: string
  operate_by: number
  operate_by_name?: string
  operate_time: string
  old_value: string | null
  new_value: string | null
  change_summary: string | null
}

export async function listAuditLogs(params: {
  page?: number
  page_size?: number
  module_type?: string
  record_id?: number
  operate_by?: number
  operate_type?: string
  start_date?: string
  end_date?: string
}): Promise<ApiResponse<AuditLogItem[]>> {
  const qs = new URLSearchParams()
  if (params.page) qs.set('page', String(params.page))
  if (params.page_size) qs.set('page_size', String(params.page_size))
  if (params.module_type) qs.set('module_type', params.module_type)
  if (params.record_id !== undefined) qs.set('record_id', String(params.record_id))
  if (params.operate_by !== undefined) qs.set('operate_by', String(params.operate_by))
  if (params.operate_type) qs.set('operate_type', params.operate_type)
  if (params.start_date) qs.set('start_date', params.start_date)
  if (params.end_date) qs.set('end_date', params.end_date)
  return api(`${PREFIX}/audit?${qs}`)
}

export async function getAuditModules(): Promise<ApiResponse<{ module_type: string; module_label: string }[]>> {
  return api(`${PREFIX}/audit/modules`)
}

// ========== 文件上传下载 ==========

export interface UploadResponse {
  file_id: string
  original_name: string
  stored_name: string
  url: string
  size: number
  content_type: string
}

export async function uploadFile(file: File): Promise<ApiResponse<UploadResponse>> {
  const formData = new FormData()
  formData.append('file', file)
  const res = await fetch(`${API_BASE}${PREFIX}/upload`, {
    method: 'POST',
    headers: { 'Authorization': 'Bearer dummy' }, // 实际项目替换真实 token
    body: formData,
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.message || `HTTP ${res.status}`)
  return data
}

export async function getDownloadUrl(filename: string): Promise<string> {
  return `${API_BASE}${PREFIX}/download/${encodeURIComponent(filename)}`
}

// ========== Excel 导入导出 ==========

export async function downloadExcelTemplate(moduleType: string): Promise<Blob> {
  const res = await fetch(`${API_BASE}${PREFIX}/excel/template/${moduleType}`, {
    headers: { 'Authorization': 'Bearer dummy' },
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.blob()
}

export async function importExcel(moduleType: string, file: File): Promise<ApiResponse<{ success: number; failed: number; errors: string[] }>> {
  const formData = new FormData()
  formData.append('file', file)
  const res = await fetch(`${API_BASE}${PREFIX}/excel/import/${moduleType}`, {
    method: 'POST',
    headers: { 'Authorization': 'Bearer dummy' },
    body: formData,
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.message || `HTTP ${res.status}`)
  return data
}

export async function exportExcel(params: {
  module_type: string
  keyword?: string
  status?: number
  start_date?: string
  end_date?: string
}): Promise<Blob> {
  const qs = new URLSearchParams()
  if (params.keyword) qs.set('keyword', params.keyword)
  if (params.status !== undefined) qs.set('status', String(params.status))
  if (params.start_date) qs.set('start_date', params.start_date)
  if (params.end_date) qs.set('end_date', params.end_date)
  const res = await fetch(`${API_BASE}${PREFIX}/excel/export/${params.module_type}?${qs}`, {
    headers: { 'Authorization': 'Bearer dummy' },
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.blob()
}